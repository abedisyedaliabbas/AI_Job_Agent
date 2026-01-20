"""
Auto Apply Engine - Actually submits applications using browser automation
Uses Selenium/Playwright to fill forms and submit applications
"""
import time
import os
from typing import Dict, Optional, List
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from job_search import JobListing
from profile_manager import ProfileManager


class AutoApplyEngine:
    """Actually submits job applications using browser automation"""
    
    def __init__(self, profile_manager: ProfileManager, headless: bool = False):
        self.profile_manager = profile_manager
        self.headless = headless
        self.driver = None
        self.profile = profile_manager.profile if profile_manager else None
        
    def _init_driver(self):
        """Initialize Selenium WebDriver"""
        if self.driver:
            return self.driver
            
        options = webdriver.ChromeOptions()
        if self.headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # User agent to appear more human
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        try:
            self.driver = webdriver.Chrome(options=options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            return self.driver
        except Exception as e:
            print(f"[ERROR] Failed to initialize Chrome driver: {e}")
            print("[INFO] Make sure ChromeDriver is installed. Install: pip install webdriver-manager")
            return None
    
    def _detect_job_board(self, url: str) -> str:
        """Detect which job board the URL belongs to"""
        url_lower = url.lower()
        if 'linkedin.com' in url_lower:
            return 'linkedin'
        elif 'indeed.com' in url_lower:
            return 'indeed'
        elif 'greenhouse.io' in url_lower or 'boards.greenhouse.io' in url_lower:
            return 'greenhouse'
        elif 'lever.co' in url_lower or 'jobs.lever.co' in url_lower:
            return 'lever'
        elif 'smartrecruiters.com' in url_lower:
            return 'smartrecruiters'
        elif 'workday.com' in url_lower:
            return 'workday'
        elif 'jobstreet' in url_lower:
            return 'jobstreet'
        else:
            return 'generic'
    
    def apply_to_job(self, job: JobListing, cover_letter: str, resume_path: Optional[str] = None) -> Dict:
        """
        Actually submit application to a job posting
        Navigates to job site, handles login/account creation, fills forms
        Returns: {'success': bool, 'status': str, 'message': str, 'requires_manual': bool, 'browser_open': bool}
        """
        if not self.profile:
            return {
                'success': False,
                'status': 'error',
                'message': 'Profile not loaded',
                'requires_manual': True,
                'browser_open': False
            }
        
        driver = self._init_driver()
        if not driver:
            return {
                'success': False,
                'status': 'error',
                'message': 'Browser automation not available. Install: pip install selenium webdriver-manager',
                'requires_manual': True,
                'browser_open': False
            }
        
        try:
            job_board = self._detect_job_board(job.url)
            print(f"[AUTO-APPLY] Detected job board: {job_board}")
            print(f"[AUTO-APPLY] Navigating to: {job.url}")
            
            # Navigate to job posting
            driver.get(job.url)
            time.sleep(3)  # Wait for page load
            
            # Try to apply based on job board type
            if job_board == 'linkedin':
                return self._apply_linkedin(driver, job, cover_letter, resume_path)
            elif job_board == 'indeed':
                return self._apply_indeed(driver, job, cover_letter, resume_path)
            elif job_board == 'greenhouse':
                return self._apply_greenhouse(driver, job, cover_letter, resume_path)
            elif job_board == 'lever':
                return self._apply_lever(driver, job, cover_letter, resume_path)
            elif job_board == 'smartrecruiters':
                return self._apply_smartrecruiters(driver, job, cover_letter, resume_path)
            else:
                return self._apply_generic(driver, job, cover_letter, resume_path)
                
        except Exception as e:
            print(f"[ERROR] Auto-apply failed: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'status': 'error',
                'message': f'Automation failed: {str(e)}. Please submit manually.',
                'requires_manual': True,
                'browser_open': True  # Browser is open, user can apply manually
            }
    
    def _apply_linkedin(self, driver, job: JobListing, cover_letter: str, resume_path: Optional[str]) -> Dict:
        """Apply to LinkedIn job posting - handles login, Easy Apply, and form filling"""
        try:
            print(f"[AUTO-APPLY] Navigating to LinkedIn job: {job.url}")
            driver.get(job.url)
            time.sleep(3)  # Wait for page load
            
            # Check if user needs to log in - wait for login and detect when complete
            login_required = False
            try:
                # Look for sign-in prompts, login buttons, or login modals
                sign_in_links = driver.find_elements(By.XPATH, 
                    "//a[contains(., 'Sign in')] | //button[contains(., 'Sign in')] | "
                    "//div[contains(., 'Sign in to see')] | //div[contains(., 'Continue with Google')] | "
                    "//div[contains(@class, 'sign-in')]"
                )
                login_modal = driver.find_elements(By.XPATH, 
                    "//div[contains(., 'Sign in to see who')] | //div[contains(., 'Continue with Google')]"
                )
                
                if (sign_in_links and any(link.is_displayed() for link in sign_in_links)) or \
                   (login_modal and any(modal.is_displayed() for modal in login_modal)):
                    login_required = True
                    print("[AUTO-APPLY] ⚠️ LinkedIn requires login.")
                    print("[AUTO-APPLY] Browser window opened. Please log in to LinkedIn (you have 30 seconds).")
                    print("[AUTO-APPLY] After logging in, the AI will automatically continue with the application.")
                    
                    # Wait for login to complete - check every 2 seconds for up to 30 seconds
                    login_complete = False
                    for attempt in range(15):  # 15 attempts * 2 seconds = 30 seconds max
                        time.sleep(2)
                        try:
                            # Check if login modal/sign-in prompts are gone
                            current_sign_in = driver.find_elements(By.XPATH, 
                                "//a[contains(., 'Sign in')] | //button[contains(., 'Sign in')] | "
                                "//div[contains(., 'Sign in to see')]"
                            )
                            # Check if we're now on the job page (Easy Apply button should be visible)
                            easy_apply_check = driver.find_elements(By.XPATH, 
                                "//button[contains(., 'Easy Apply')] | //button[contains(., 'Apply')]"
                            )
                            
                            # If sign-in prompts are gone OR Easy Apply button is visible, login is complete
                            if (not any(link.is_displayed() for link in current_sign_in) or 
                                any(btn.is_displayed() for btn in easy_apply_check)):
                                login_complete = True
                                print("[AUTO-APPLY] ✅ Login detected! Continuing with application...")
                                time.sleep(2)  # Brief pause after login
                                break
                        except:
                            pass
                        
                        if attempt % 5 == 0:  # Every 10 seconds, remind user
                            print(f"[AUTO-APPLY] Still waiting for login... ({attempt * 2} seconds elapsed)")
                    
                    if not login_complete:
                        print("[AUTO-APPLY] ⚠️ Login timeout. Please log in manually and the AI will continue.")
                        # Refresh and try to continue anyway
                        driver.refresh()
                        time.sleep(3)
            except Exception as e:
                print(f"[AUTO-APPLY] Login detection error: {e}")
                pass
            
            # Look for "Easy Apply" button - try multiple selectors with better post-login handling
            easy_apply_btn = None
            try:
                # If login was required, refresh page and wait longer for page to fully load
                if login_required:
                    print("[AUTO-APPLY] Refreshing page after login to ensure Easy Apply button is visible...")
                    driver.refresh()
                    time.sleep(4)  # Wait for page to fully reload after login
                    
                    # Also try navigating to the job URL again to ensure we're on the right page
                    print("[AUTO-APPLY] Navigating to job URL again to ensure correct page...")
                    driver.get(job.url)
                    time.sleep(3)
                
                # Try multiple ways to find the Easy Apply button with longer timeout after login
                selectors = [
                    "//button[contains(., 'Easy Apply')]",
                    "//button[contains(., 'Apply') and not(contains(., 'Save'))]",
                    "//span[contains(., 'Easy Apply')]/ancestor::button",
                    "//a[contains(., 'Easy Apply')]",
                    "//button[@aria-label='Easy Apply']",
                    "//button[@data-control-name='jobdetails_topcard_inapply']",
                    "//button[contains(@class, 'jobs-apply-button')]",
                    "//button[contains(@class, 'apply-button')]",
                    "//button[contains(., 'Apply')]"
                ]
                
                # Wait longer if login was required (page might need more time to load)
                wait_time = 10 if login_required else 5
                
                print(f"[AUTO-APPLY] Looking for Easy Apply button (timeout: {wait_time}s)...")
                for selector in selectors:
                    try:
                        easy_apply_btn = WebDriverWait(driver, wait_time).until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                        if easy_apply_btn and easy_apply_btn.is_displayed():
                            print(f"[AUTO-APPLY] ✅ Found Easy Apply button using selector: {selector[:60]}")
                            break
                    except:
                        continue
                
                # If still not found, try scrolling down (LinkedIn sometimes hides it below fold)
                if not easy_apply_btn:
                    print("[AUTO-APPLY] Easy Apply button not immediately visible. Scrolling page...")
                    driver.execute_script("window.scrollTo(0, 500);")
                    time.sleep(2)
                    driver.execute_script("window.scrollTo(0, 0);")  # Scroll back up
                    time.sleep(1)
                    
                    # Try again after scrolling
                    for selector in selectors:
                        try:
                            easy_apply_btn = driver.find_element(By.XPATH, selector)
                            if easy_apply_btn and easy_apply_btn.is_displayed():
                                print(f"[AUTO-APPLY] ✅ Found Easy Apply button after scrolling")
                                break
                        except:
                            continue
                
                if not easy_apply_btn:
                    print("[AUTO-APPLY] ⚠️ Easy Apply button not found. Possible reasons:")
                    print("[AUTO-APPLY]   1. Job doesn't have Easy Apply feature")
                    print("[AUTO-APPLY]   2. You need to be logged in (please check browser)")
                    print("[AUTO-APPLY]   3. Job requires application through company website")
                    print("[AUTO-APPLY]   4. Page hasn't fully loaded yet")
                    return {
                        'success': False,
                        'status': 'no_easy_apply',
                        'message': 'This job does not have Easy Apply. Please apply manually through the company website. The browser window is open for you to complete the application.',
                        'requires_manual': True,
                        'browser_open': True
                    }
                
                print("[AUTO-APPLY] Clicking Easy Apply button...")
                # Scroll to button to ensure it's in view
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", easy_apply_btn)
                time.sleep(1)
                easy_apply_btn.click()
                time.sleep(5)  # Wait for form to load (increased for reliability)
                
            except TimeoutException:
                return {
                    'success': False,
                    'status': 'timeout',
                    'message': 'Could not find Easy Apply button. The job may require manual application.',
                    'requires_manual': True
                }
            
            # Fill in application form - try multiple field selectors
            filled_fields = []
            
            # Name - try multiple selectors
            name_selectors = [
                (By.NAME, "name"),
                (By.ID, "name"),
                (By.ID, "first-name"),
                (By.NAME, "firstName"),
                (By.XPATH, "//input[@placeholder*='First name' or @placeholder*='Name']")
            ]
            for by, selector in name_selectors:
                try:
                    name_field = driver.find_element(by, selector)
                    if name_field.is_displayed():
                        name_field.clear()
                        name_field.send_keys(self.profile.name.split()[0] if self.profile.name else "")
                        filled_fields.append("name")
                        break
                except:
                    continue
            
            # Email - try multiple selectors
            email_selectors = [
                (By.NAME, "email"),
                (By.ID, "email"),
                (By.NAME, "emailAddress"),
                (By.XPATH, "//input[@type='email']")
            ]
            for by, selector in email_selectors:
                try:
                    email_field = driver.find_element(by, selector)
                    if email_field.is_displayed():
                        email_field.clear()
                        email_field.send_keys(self.profile.email)
                        filled_fields.append("email")
                        break
                except:
                    continue
            
            # Phone - try multiple selectors
            phone_selectors = [
                (By.NAME, "phone"),
                (By.ID, "phone"),
                (By.NAME, "phoneNumber"),
                (By.XPATH, "//input[@type='tel' or @placeholder*='Phone']")
            ]
            for by, selector in phone_selectors:
                try:
                    phone_field = driver.find_element(by, selector)
                    if phone_field.is_displayed():
                        phone_field.clear()
                        phone_field.send_keys(self.profile.phone or "")
                        filled_fields.append("phone")
                        break
                except:
                    continue
            
            # Cover letter - try multiple selectors
            cover_selectors = [
                (By.NAME, "coverLetter"),
                (By.ID, "coverLetter"),
                (By.NAME, "message"),
                (By.XPATH, "//textarea[@placeholder*='cover' or @placeholder*='message' or @aria-label*='cover']"),
                (By.TAG_NAME, "textarea")
            ]
            for by, selector in cover_selectors:
                try:
                    cover_field = driver.find_element(by, selector)
                    if cover_field.is_displayed():
                        cover_field.clear()
                        cover_field.send_keys(cover_letter)
                        filled_fields.append("cover_letter")
                        break
                except:
                    continue
            
            # Upload resume if provided
            if resume_path and os.path.exists(resume_path):
                try:
                    resume_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='file']")
                    for resume_input in resume_inputs:
                        if resume_input.is_displayed():
                            resume_input.send_keys(os.path.abspath(resume_path))
                            time.sleep(2)
                            filled_fields.append("resume")
                            break
                except:
                    pass
            
            print(f"[AUTO-APPLY] Filled fields: {', '.join(filled_fields)}")
            
            # AUTO-SUBMIT: Actually click the submit button to complete the application
            print(f"[AUTO-APPLY] Attempting to submit application automatically...")
            time.sleep(2)  # Brief pause to ensure form is fully loaded
            
            # Look for submit button - try multiple selectors (LinkedIn-specific)
            submit_btn = None
            submit_selectors = [
                # LinkedIn Easy Apply specific selectors
                "//button[contains(., 'Submit application')]",
                "//button[contains(., 'Submit') and not(contains(., 'Review'))]",
                "//button[@aria-label*='Submit' or @aria-label*='Submit application']",
                "//span[contains(., 'Submit application')]/ancestor::button",
                "//span[contains(., 'Submit')]/ancestor::button[not(contains(., 'Review'))]",
                # Generic selectors
                "//button[@type='submit']",
                "//button[contains(@class, 'submit')]",
                "//button[contains(@class, 'apply')]",
                "//button[contains(., 'Send')]",
                "//span[contains(., 'Send')]/ancestor::button"
            ]
            
            # Try to find and click submit button
            for selector in submit_selectors:
                try:
                    submit_btn = driver.find_element(By.XPATH, selector)
                    if submit_btn and submit_btn.is_displayed() and submit_btn.is_enabled():
                        print(f"[AUTO-APPLY] ✅ Found submit button: '{submit_btn.text[:50]}'")
                        
                        # Scroll to button to ensure it's in view
                        driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
                        time.sleep(0.5)
                        
                        # Click the submit button
                        print(f"[AUTO-APPLY] Clicking submit button...")
                        submit_btn.click()
                        time.sleep(4)  # Wait for submission to process
                        
                        # Check if submission was successful
                        try:
                            # Check for success indicators
                            success_indicators = driver.find_elements(By.XPATH, 
                                "//*[contains(., 'success') or contains(., 'submitted') or contains(., 'applied') or "
                                "contains(., 'thank you') or contains(., 'Application sent') or "
                                "contains(., 'Your application has been')]"
                            )
                            current_url = driver.current_url.lower()
                            if (success_indicators and any(ind.is_displayed() for ind in success_indicators)) or \
                               'submitted' in current_url or 'success' in current_url or 'applied' in current_url:
                                print("[AUTO-APPLY] ✅ Application submitted successfully!")
                                return {
                                    'success': True,
                                    'status': 'submitted',
                                    'message': f'✅ Application submitted successfully! Form filled with {len(filled_fields)} fields and automatically submitted.',
                                    'requires_manual': False,
                                    'browser_open': True,
                                    'filled_fields': filled_fields,
                                    'submitted': True
                                }
                        except:
                            pass
                        
                        # If we clicked submit, assume it worked (LinkedIn often doesn't show explicit success)
                        print("[AUTO-APPLY] ✅ Submit button clicked - application should be submitted")
                        return {
                            'success': True,
                            'status': 'submitted',
                            'message': f'✅ Application submitted! Form filled with {len(filled_fields)} fields and submit button clicked automatically. Check the browser to confirm.',
                            'requires_manual': False,
                            'browser_open': True,
                            'filled_fields': filled_fields,
                            'submitted': True
                        }
                except Exception as e:
                    continue
            
            # If no submit button found, form might be multi-step - try "Next" button
            print("[AUTO-APPLY] Submit button not found. Checking for multi-step form (Next/Continue buttons)...")
            next_btn = None
            next_selectors = [
                "//button[contains(., 'Next')]",
                "//button[contains(., 'Continue')]",
                "//button[@aria-label*='Next' or @aria-label*='Continue']",
                "//span[contains(., 'Next')]/ancestor::button",
                "//span[contains(., 'Continue')]/ancestor::button"
            ]
            
            for selector in next_selectors:
                try:
                    next_btn = driver.find_element(By.XPATH, selector)
                    if next_btn and next_btn.is_displayed() and next_btn.is_enabled():
                        print(f"[AUTO-APPLY] Found Next/Continue button (multi-step form), clicking...")
                        driver.execute_script("arguments[0].scrollIntoView(true);", next_btn)
                        time.sleep(0.5)
                        next_btn.click()
                        time.sleep(3)  # Wait for next step to load
                        
                        # Try to find submit button again after clicking Next
                        print("[AUTO-APPLY] Looking for submit button on next step...")
                        for selector in submit_selectors:
                            try:
                                submit_btn = driver.find_element(By.XPATH, selector)
                                if submit_btn and submit_btn.is_displayed() and submit_btn.is_enabled():
                                    print(f"[AUTO-APPLY] ✅ Found submit button on next step, clicking...")
                                    driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
                                    time.sleep(0.5)
                                    submit_btn.click()
                                    time.sleep(4)
                                    return {
                                        'success': True,
                                        'status': 'submitted',
                                        'message': f'✅ Application submitted! Multi-step form completed and submitted automatically.',
                                        'requires_manual': False,
                                        'browser_open': True,
                                        'filled_fields': filled_fields,
                                        'submitted': True
                                    }
                            except:
                                continue
                        
                        # If we clicked Next but no submit found, might need to fill more fields or click Next again
                        print("[AUTO-APPLY] No submit button found after Next. Checking for more steps...")
                        # Try clicking Next one more time if available
                        try:
                            next_btn2 = driver.find_element(By.XPATH, selector)
                            if next_btn2 and next_btn2.is_displayed() and next_btn2.is_enabled():
                                print("[AUTO-APPLY] Clicking Next again...")
                                next_btn2.click()
                                time.sleep(3)
                                # Look for submit again
                                for selector in submit_selectors:
                                    try:
                                        submit_btn = driver.find_element(By.XPATH, selector)
                                        if submit_btn and submit_btn.is_displayed() and submit_btn.is_enabled():
                                            print("[AUTO-APPLY] ✅ Found submit after second Next, clicking...")
                                            submit_btn.click()
                                            time.sleep(4)
                                            return {
                                                'success': True,
                                                'status': 'submitted',
                                                'message': f'✅ Application submitted! Multi-step form completed.',
                                                'requires_manual': False,
                                                'browser_open': True,
                                                'filled_fields': filled_fields,
                                                'submitted': True
                                            }
                                    except:
                                        continue
                        except:
                            pass
                        
                        # If still no submit, return in_progress status
                        return {
                            'success': True,
                            'status': 'in_progress',
                            'message': f'Form filled ({len(filled_fields)} fields) and advanced through steps. Please check browser and complete remaining steps if needed.',
                            'requires_manual': False,
                            'browser_open': True,
                            'filled_fields': filled_fields
                        }
                except:
                    continue
            
            # If no submit or next button found, form might be already submitted or needs manual completion
            return {
                'success': True,
                'status': 'form_filled',
                'message': f'Form filled ({len(filled_fields)} fields). Could not find submit button - please check browser and submit manually if needed.',
                'requires_manual': False,
                'browser_open': True,
                'filled_fields': filled_fields
            }
            
        except Exception as e:
            print(f"[AUTO-APPLY] LinkedIn error: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'status': 'error',
                'message': f'Error during LinkedIn application: {str(e)}. Please apply manually.',
                'requires_manual': True
            }
    
    def _apply_indeed(self, driver, job: JobListing, cover_letter: str, resume_path: Optional[str]) -> Dict:
        """Apply to Indeed job posting"""
        try:
            # Click "Apply now" button
            apply_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(., 'Apply now')] | //button[contains(., 'Apply')]"))
            )
            apply_btn.click()
            time.sleep(3)
            
            # Indeed often redirects to external site
            # Fill form if on Indeed's application page
            try:
                # Name
                name_field = driver.find_element(By.ID, "input-applicant.name") or driver.find_element(By.NAME, "name")
                name_field.send_keys(self.profile.name)
            except:
                pass
            
            # Email
            try:
                email_field = driver.find_element(By.ID, "input-applicant.email") or driver.find_element(By.NAME, "email")
                email_field.send_keys(self.profile.email)
            except:
                pass
            
            # Cover letter
            try:
                cover_field = driver.find_element(By.ID, "input-applicant.applicationMessage") or driver.find_element(By.NAME, "message")
                cover_field.send_keys(cover_letter)
            except:
                pass
            
            return {
                'success': True,
                'status': 'ready_for_review',
                'message': 'Application form filled. Please review and submit.',
                'requires_manual': False,
                'browser_open': True
            }
            
        except TimeoutException:
            return {
                'success': False,
                'status': 'timeout',
                'message': 'Could not find application form. Please apply manually.',
                'requires_manual': True
            }
    
    def _apply_greenhouse(self, driver, job: JobListing, cover_letter: str, resume_path: Optional[str]) -> Dict:
        """Apply to Greenhouse job posting"""
        try:
            # Greenhouse has a standard form structure
            # First name
            try:
                first_name = driver.find_element(By.ID, "first_name")
                first_name.send_keys(self.profile.name.split()[0] if self.profile.name else "")
            except:
                pass
            
            # Last name
            try:
                last_name = driver.find_element(By.ID, "last_name")
                last_name.send_keys(" ".join(self.profile.name.split()[1:]) if len(self.profile.name.split()) > 1 else "")
            except:
                pass
            
            # Email
            try:
                email = driver.find_element(By.ID, "email")
                email.send_keys(self.profile.email)
            except:
                pass
            
            # Phone
            try:
                phone = driver.find_element(By.ID, "phone")
                phone.send_keys(self.profile.phone)
            except:
                pass
            
            # Cover letter
            try:
                cover = driver.find_element(By.ID, "cover_letter")
                cover.send_keys(cover_letter)
            except:
                pass
            
            # Resume upload
            if resume_path and os.path.exists(resume_path):
                try:
                    resume_input = driver.find_element(By.CSS_SELECTOR, "input[type='file']")
                    resume_input.send_keys(os.path.abspath(resume_path))
                    time.sleep(2)
                except:
                    pass
            
            return {
                'success': True,
                'status': 'ready_for_review',
                'message': 'Greenhouse form filled. Please review and submit.',
                'requires_manual': False,
                'browser_open': True
            }
            
        except Exception as e:
            return {
                'success': False,
                'status': 'error',
                'message': f'Could not fill Greenhouse form: {str(e)}',
                'requires_manual': True
            }
    
    def _apply_lever(self, driver, job: JobListing, cover_letter: str, resume_path: Optional[str]) -> Dict:
        """Apply to Lever job posting"""
        # Similar to Greenhouse
        return self._apply_greenhouse(driver, job, cover_letter, resume_path)
    
    def _apply_smartrecruiters(self, driver, job: JobListing, cover_letter: str, resume_path: Optional[str]) -> Dict:
        """Apply to SmartRecruiters job posting"""
        try:
            # Click apply button
            apply_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Apply')] | //a[contains(., 'Apply')]"))
            )
            apply_btn.click()
            time.sleep(2)
            
            # Fill form fields
            try:
                name_field = driver.find_element(By.NAME, "name") or driver.find_element(By.ID, "name")
                name_field.send_keys(self.profile.name)
            except:
                pass
            
            try:
                email_field = driver.find_element(By.NAME, "email") or driver.find_element(By.ID, "email")
                email_field.send_keys(self.profile.email)
            except:
                pass
            
            try:
                cover_field = driver.find_element(By.NAME, "coverLetter") or driver.find_element(By.TAG_NAME, "textarea")
                cover_field.send_keys(cover_letter)
            except:
                pass
            
            return {
                'success': True,
                'status': 'ready_for_review',
                'message': 'SmartRecruiters form filled. Please review and submit.',
                'requires_manual': False,
                'browser_open': True
            }
            
        except:
            return {
                'success': False,
                'status': 'error',
                'message': 'Could not fill SmartRecruiters form. Please apply manually.',
                'requires_manual': True
            }
    
    def _apply_generic(self, driver, job: JobListing, cover_letter: str, resume_path: Optional[str]) -> Dict:
        """Generic application attempt - tries to find common form fields"""
        try:
            # Try to find and fill common fields
            fields_filled = 0
            
            # Name field
            for selector in ["input[name='name']", "input[id='name']", "input[placeholder*='name' i]"]:
                try:
                    field = driver.find_element(By.CSS_SELECTOR, selector)
                    field.send_keys(self.profile.name)
                    fields_filled += 1
                    break
                except:
                    continue
            
            # Email field
            for selector in ["input[type='email']", "input[name='email']", "input[id='email']"]:
                try:
                    field = driver.find_element(By.CSS_SELECTOR, selector)
                    field.send_keys(self.profile.email)
                    fields_filled += 1
                    break
                except:
                    continue
            
            # Cover letter
            try:
                textarea = driver.find_element(By.TAG_NAME, "textarea")
                textarea.send_keys(cover_letter)
                fields_filled += 1
            except:
                pass
            
            if fields_filled > 0:
                return {
                    'success': True,
                    'status': 'partially_filled',
                    'message': f'Filled {fields_filled} field(s). Please complete the form manually.',
                    'requires_manual': True,
                    'browser_open': True
                }
            else:
                return {
                    'success': False,
                    'status': 'no_form_found',
                    'message': 'Could not detect application form. Please apply manually.',
                    'requires_manual': True
                }
                
        except Exception as e:
            return {
                'success': False,
                'status': 'error',
                'message': f'Generic application failed: {str(e)}',
                'requires_manual': True
            }
    
    def close(self):
        """Close browser"""
        if self.driver:
            # Don't close - let user review
            # self.driver.quit()
            pass
    
    def __del__(self):
        """Cleanup"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
