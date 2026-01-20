"""
Automated Job Agent - Automatically finds and applies to jobs based on resume
"""
from profile_manager import ProfileManager
from job_search import JobSearchEngine, JobListing
from job_matcher import JobMatcher
from cover_letter_generator import CoverLetterGenerator
from application_automator import ApplicationAutomator
from worldwide_job_search import WorldwideJobSearch
from fast_job_search import FastJobSearch
from simple_job_search import SimpleJobSearch
from google_job_search import GoogleJobSearch
from comprehensive_job_search import ComprehensiveJobSearch
from typing import List, Dict
import json
import time
import re


class AutoJobAgent:
    """Automated AI agent that finds and applies to jobs automatically"""
    
    def __init__(self, profile_manager: ProfileManager):
        self.profile_manager = profile_manager
        self.job_search = JobSearchEngine()
        self.job_search.worldwide_search = WorldwideJobSearch()
        self.fast_search = FastJobSearch()
        self.simple_search = SimpleJobSearch()
        self.google_search = GoogleJobSearch()  # Google-based search (fallback)
        self.comprehensive_search = ComprehensiveJobSearch()  # NEW: Comprehensive multi-source search (1000+ jobs)
        self.job_matcher = JobMatcher(profile_manager)
        self.cover_letter_gen = CoverLetterGenerator(profile_manager)
        self.application_automator = ApplicationAutomator(profile_manager, self.cover_letter_gen)
        
    def extract_keywords_from_profile(self) -> List[str]:
        """Extract search keywords from user's profile - cleaned and meaningful"""
        keywords = []
        
        # FIRST: Check if user has custom job keywords (highest priority)
        if hasattr(self.profile_manager.profile, 'job_keywords') and self.profile_manager.profile.job_keywords:
            custom_keywords = [k.strip() for k in self.profile_manager.profile.job_keywords if k.strip()]
            if custom_keywords:
                print(f"[AUTO AGENT] Using custom job keywords: {custom_keywords[:5]}")
                return custom_keywords[:10]  # Use up to 10 custom keywords
        
        # Extract from skills (most reliable source) - prioritize technical skills
        known_tech_skills = {
            'python', 'java', 'javascript', 'c++', 'c#', 'sql', 'html', 'css', 'r', 'matlab', 'scala', 'go', 'rust',
            'dft', 'tddft', 'gaussian', 'orca', 'vasp', 'materials', 'studio', 'gromacs', 'amber', 'charmm', 'namd',
            'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy', 'matplotlib', 'seaborn', 'jupyter', 'spark',
            'linux', 'unix', 'windows', 'macos', 'docker', 'kubernetes', 'aws', 'azure', 'gcp',
            'mongodb', 'postgresql', 'mysql', 'redis', 'elasticsearch',
            'react', 'angular', 'vue', 'node.js', 'django', 'flask', 'spring', 'express'
        }
        
        for skill_cat in self.profile_manager.profile.skills:
            if skill_cat.skills:
                for skill in skill_cat.skills:
                    # Clean skill: remove category headers, bullet points, special chars
                    skill_clean = skill.lower().strip()
                    skill_clean = skill_clean.replace('•', '').replace('&', '').replace(':', '').strip()
                    
                    # Skip category headers
                    if any(word in skill_clean for word in ['category', 'technical', 'expertise', 'skills']):
                        continue
                    
                    # If it's a known technical skill, add it directly
                    if skill_clean in known_tech_skills:
                        keywords.append(skill_clean)
                    else:
                        # Extract meaningful words (4+ chars, not common words)
                        skill_words = [w for w in skill_clean.split() if len(w) >= 4]
                        keywords.extend(skill_words[:3])  # Top 3 per skill
        
        # Extract from experience titles - focus on job roles and fields
        # BUT filter out generic job title words AND description words
        generic_job_words = {
            'postdoctoral', 'postdoc', 'undergraduate', 'graduate', 'senior', 'junior', 
            'lead', 'principal', 'assistant', 'associate', 'visiting', 'research', 
            'researcher', 'scientist', 'engineer', 'fellow', 'position', 'role',
            'successfully', 'performance', 'nature', 'communications', 'optimization',
            'success', 'successful', 'perform', 'performing', 'natural', 'communicate'
        }
        
        job_role_keywords = []
        for exp in self.profile_manager.profile.experience:
            if exp.title:
                title_clean = exp.title.lower().strip()
                # Remove common prefixes
                title_clean = re.sub(r'^(visiting|postdoctoral|postdoc|senior|junior|lead|principal|assistant|associate)\s+', '', title_clean)
                # Extract key terms (4+ chars) but filter out generic words
                title_words = [w for w in title_clean.split() 
                             if len(w) >= 4 and w not in generic_job_words]
                # Only add meaningful technical terms
                for word in title_words[:2]:
                    if word not in ['successfully', 'performance', 'nature', 'communications', 'optimization']:
                        job_role_keywords.append(word)
        
        keywords.extend(job_role_keywords)
        
        # Extract from education field - focus on SPECIFIC field of study, not generic terms
        generic_edu_words = {
            'undergraduate', 'graduate', 'bachelor', 'master', 'phd', 'doctorate',
            'degree', 'program', 'programme', 'studies', 'science', 'engineering',
            'mathematics', 'math', 'physics', 'chemistry', 'biology'  # Too generic
        }
        
        for edu in self.profile_manager.profile.education:
            if edu.field:
                field_clean = edu.field.lower().strip()
                # Extract meaningful terms (4+ chars) but skip generic words
                field_words = [w for w in field_clean.split() 
                             if len(w) >= 4 and w not in generic_edu_words]
                # Only add if we have specific terms (not just generic "engineering" or "mathematics")
                if field_words:
                    keywords.extend(field_words[:3])  # Top 3 per education
                # If field contains compound terms like "computational chemistry", extract those
                if 'computational' in field_clean or 'applied' in field_clean or 'theoretical' in field_clean:
                    # Extract compound terms
                    compound_terms = re.findall(r'(computational|applied|theoretical|quantum|molecular|organic|inorganic)\s+(\w+)', field_clean)
                    for modifier, term in compound_terms:
                        if len(term) >= 4 and term not in generic_edu_words:
                            keywords.append(f"{modifier} {term}")
        
        # Remove duplicates and common/generic words - EXPANDED list
        common_words = {
            'the', 'and', 'or', 'for', 'with', 'from', 'that', 'this', 'are', 'was', 'from', 'in', 'at', 'on', 'to', 'of', 'a', 'an',
            # Generic job titles
            'position', 'researcher', 'scientist', 'engineer', 'manager', 'director', 'analyst', 'specialist', 'coordinator', 
            'developer', 'consultant', 'assistant', 'associate', 'senior', 'junior', 'lead', 'principal',
            'postdoctoral', 'postdoc', 'undergraduate', 'graduate', 'fellow', 'visiting',
            # Generic tech terms
            'data', 'system', 'systems', 'software', 'application', 'applications', 'technology', 'technologies', 'service', 'services',
            # Generic action words and adverbs
            'work', 'working', 'experience', 'skills', 'skill', 'expertise', 'knowledge', 'ability', 'abilities',
            'research', 'developing', 'creating', 'designing', 'implementing', 'using', 'utilizing',
            'successfully', 'performance', 'nature', 'communications', 'communication', 'optimization', 'optimize',
            'success', 'successful', 'perform', 'performing', 'natural', 'communicate', 'optimize', 'optimizing',
            # Institution words
            'university', 'college', 'institute', 'department', 'school', 'program', 'programme',
            # Generic academic terms
            'mathematics', 'math', 'engineering', 'science', 'physics', 'chemistry', 'biology',
            'bachelor', 'master', 'phd', 'doctorate', 'degree', 'studies',
            # Generic descriptive words
            'method', 'methods', 'approach', 'approaches', 'technique', 'techniques', 'process', 'processes',
            'analysis', 'analyses', 'study', 'studies', 'project', 'projects', 'work', 'works'
        }
        keywords = [k for k in keywords if k not in common_words and len(k) >= 4]  # Minimum 4 chars
        
        # Get top keywords by frequency, prioritizing longer/more specific terms
        from collections import Counter
        keyword_counts = Counter(keywords)
        
        # Prioritize longer keywords (more specific) and higher frequency
        scored_keywords = []
        for word, count in keyword_counts.items():
            # Score: frequency * length^2 (heavily favor longer, more specific terms)
            score = count * (len(word) ** 2)
            scored_keywords.append((word, score))
        
        # Sort by score (highest first)
        scored_keywords.sort(key=lambda x: x[1], reverse=True)
        top_keywords = [word for word, score in scored_keywords[:15]]
        
        # Final filtering: remove any remaining generic terms - STRICTER
        final_keywords = []
        generic_job_words = {
            'postdoctoral', 'postdoc', 'undergraduate', 'graduate', 'senior', 'junior', 
            'lead', 'principal', 'assistant', 'associate', 'visiting', 'research', 
            'researcher', 'scientist', 'engineer', 'fellow', 'position', 'role',
            'developer', 'analyst', 'specialist', 'coordinator', 'consultant', 'manager'
        }
        generic_edu_words = {
            'undergraduate', 'graduate', 'bachelor', 'master', 'phd', 'doctorate',
            'degree', 'program', 'programme', 'studies', 'science', 'engineering',
            'mathematics', 'math', 'physics', 'chemistry', 'biology'
        }
        
        # Additional generic single words to filter
        generic_single_words = {
            'research', 'engineering', 'mathematics', 'science', 'physics', 'chemistry',
            'biology', 'data', 'system', 'software', 'application', 'technology'
        }
        
        for kw in top_keywords:
            kw_lower = kw.lower().strip()
            # Skip if it's still a generic term
            if kw_lower in common_words or kw_lower in generic_job_words or kw_lower in generic_edu_words:
                continue
            # Skip single generic words that don't add value
            if kw_lower in generic_single_words:
                continue
            # Skip if it's just a single word and not a known tech term
            if ' ' not in kw and kw_lower not in known_tech_skills:
                # Check if it's a meaningful technical term (at least 5 chars, not common word)
                if len(kw_lower) < 5 or kw_lower in ['work', 'study', 'field', 'area']:
                    continue
            final_keywords.append(kw)
        
        # If we have good keywords, use them; otherwise use skills-based fallback
        if final_keywords:
            return final_keywords[:8]  # Return top 8 keywords
        else:
            # Fallback: try to extract from skills only
            skill_keywords = []
            for skill_cat in self.profile_manager.profile.skills:
                if skill_cat.skills:
                    for skill in skill_cat.skills[:5]:  # Top 5 skills
                        skill_clean = skill.lower().strip()
                        if skill_clean in known_tech_skills:
                            skill_keywords.append(skill_clean)
            
            if skill_keywords:
                return skill_keywords[:5]
            else:
                # Last resort: very generic but better than nothing
                return ["computational", "research", "chemistry"]
    
    def auto_search_and_apply(self, max_jobs: int = 10, min_match_score: float = 0.6, 
                              auto_apply: bool = False) -> Dict:
        """Automatically search for jobs and optionally apply"""
        results = {
            'searched': False,
            'jobs_found': 0,
            'jobs_matched': 0,
            'cover_letters_generated': 0,
            'applications_sent': 0,
            'jobs': []
        }
        
        try:
            # Extract keywords from profile
            keywords = self.extract_keywords_from_profile()
            location = self.profile_manager.profile.location or "Worldwide"
            
            print(f"[AUTO AGENT] Searching for jobs with keywords: {keywords}")
            print(f"[AUTO AGENT] Location: {location}")
            
            # USE AI/ML-POWERED JOB DISCOVERY FIRST
            jobs = []
            
            # Step 1: AI-Powered Job Discovery (uses ML to find company websites)
            try:
                from ai_job_discovery import AIJobDiscovery
                print(f"[AUTO AGENT] Using AI/ML to discover jobs from company websites...")
                ai_discovery = AIJobDiscovery()
                ai_jobs = ai_discovery.discover_jobs_ai(keywords, location, max_jobs * 3)
                if ai_jobs:
                    jobs.extend(ai_jobs)
                    print(f"[AUTO AGENT] AI discovery found: {len(ai_jobs)} jobs from company websites")
            except ImportError:
                print(f"[AUTO AGENT] AI discovery not available (install: pip install sentence-transformers scikit-learn)")
            except Exception as e:
                print(f"[AUTO AGENT] AI discovery failed: {e}")
                import traceback
                traceback.print_exc()
            
            # Step 2: Google search - finds direct company website jobs
            try:
                print(f"[AUTO AGENT] Searching Google for company website jobs...")
                google_jobs = self.google_search.search(
                    keywords, location, max_jobs * 5  # Get more from Google
                )
                if google_jobs:
                    jobs.extend(google_jobs)
                    print(f"[AUTO AGENT] Google search found: {len(google_jobs)} jobs (prioritizing company websites)")
            except Exception as e:
                print(f"[AUTO AGENT] Google search failed: {e}")
                import traceback
                traceback.print_exc()
            
            # Step 3: Comprehensive search (includes Indeed, Glassdoor, etc. - but NOT LinkedIn)
            try:
                # Search for more jobs than requested to account for duplicates and filtering
                # Request 10x to ensure we get enough after deduplication and matching
                search_limit = max(max_jobs * 10, 100)  # At least 100 jobs, or 10x requested
                comprehensive_jobs = self.comprehensive_search.search(
                    keywords, location, search_limit
                )
                if comprehensive_jobs:
                    jobs.extend(comprehensive_jobs)
                    print(f"[AUTO AGENT] Comprehensive search found: {len(comprehensive_jobs)} jobs")
            except Exception as e:
                print(f"[AUTO AGENT] Comprehensive search failed: {e}")
                import traceback
                traceback.print_exc()
            
            # Remove duplicates (Google jobs might overlap with comprehensive)
            seen = set()
            unique_jobs = []
            for job in jobs:
                key = (job.title.lower().strip(), job.company.lower().strip())
                if key not in seen:
                    seen.add(key)
                    unique_jobs.append(job)
            
            # PRIORITIZE company websites, but KEEP ALL jobs (including LinkedIn)
            # LinkedIn jobs are still useful - user can apply manually or we can try auto-apply
            def job_priority(job):
                url_lower = (job.url or "").lower()
                # LinkedIn gets lower priority but is KEPT
                if 'linkedin.com' in url_lower:
                    return 1  # Lower priority but included
                # Higher priority for company websites
                elif any(board in url_lower for board in ['indeed.com', 'glassdoor.com', 'monster.com', 'ziprecruiter.com']):
                    return 2  # Medium priority
                else:
                    return 3  # Highest priority (company websites, direct links)
            
            # Sort by priority (highest first) - but KEEP ALL jobs
            jobs = sorted(unique_jobs, key=lambda j: (job_priority(j), j.source or ""), reverse=True)
            print(f"[AUTO AGENT] Total unique jobs found: {len(jobs)}")
            
            # Count by source
            source_counts = {}
            for job in jobs:
                source = job.source or "unknown"
                source_counts[source] = source_counts.get(source, 0) + 1
            print(f"[AUTO AGENT] Jobs by source: {source_counts}")
            
            # FINAL FALLBACK: If still no jobs, try with simplified keywords
            if len(jobs) == 0 and keywords:
                print(f"[AUTO AGENT] No jobs found with current keywords. Trying simplified search...")
                # Use only the top 3 most specific keywords, or use generic terms
                simplified_keywords = keywords[:3] if len(keywords) >= 3 else keywords
                # Also try generic job search terms
                fallback_terms = ['researcher', 'scientist', 'chemistry', 'computational']
                combined_keywords = simplified_keywords + [t for t in fallback_terms if t not in simplified_keywords]
                
                try:
                    print(f"[AUTO AGENT] Fallback search with: {combined_keywords[:5]}")
                    fallback_jobs = self.comprehensive_search.search(
                        combined_keywords[:5], location, max_jobs * 3
                    )
                    if fallback_jobs:
                        jobs.extend(fallback_jobs)
                        print(f"[AUTO AGENT] Fallback search found: {len(fallback_jobs)} jobs")
                except Exception as e:
                    print(f"[AUTO AGENT] Fallback search failed: {e}")
            
            # If still not enough, try simple search as last resort
            if len(jobs) < max_jobs:
                try:
                    simple_jobs = self.simple_search.search(
                        keywords, location, max_jobs * 2
                    )
                    # Merge without duplicates
                    existing_titles = {(j.title.lower(), j.company.lower()) for j in jobs}
                    for job in simple_jobs:
                        key = (job.title.lower(), job.company.lower())
                        if key not in existing_titles:
                            jobs.append(job)
                            existing_titles.add(key)
                    print(f"[AUTO AGENT] Simple search added: {len(simple_jobs)} more jobs")
                except Exception as e:
                    print(f"[AUTO AGENT] Simple search failed: {e}")
            
            # If no jobs found, provide helpful message
            if len(jobs) == 0:
                print(f"[AUTO AGENT] No jobs found via automated search.")
                print(f"[AUTO AGENT] Keywords used: {keywords}")
                print(f"[AUTO AGENT] Location: {location}")
                print(f"[AUTO AGENT] This is common - job boards block automated scraping.")
                results['error'] = f"No jobs found via automated search. Job boards often block automated scraping. Try: 1) Use 'Add Job' to add jobs by URL, 2) Visit job boards directly (Indeed, LinkedIn), 3) Search manually and copy job URLs. Keywords: {', '.join(keywords[:3])}"
            else:
                # Jobs were found (even if just search URLs)
                print(f"[AUTO AGENT] Found {len(jobs)} job listings/search URLs")
            
            results['jobs_found'] = len(jobs)
            results['searched'] = True
            
            if not jobs:
                print(f"[AUTO AGENT] No jobs found. Keywords used: {keywords}")
                return results
            
            # Match jobs to profile (lower threshold if not many matches)
            print(f"[AUTO AGENT] Matching {len(jobs)} jobs to profile...")
            matched_jobs = self.job_matcher.match_jobs(jobs, min_score=min_match_score)
            
            # If not enough matches, lower threshold
            if len(matched_jobs) < max_jobs // 2:
                matched_jobs = self.job_matcher.match_jobs(jobs, min_score=0.3)
            
            matched_jobs.sort(key=lambda j: j.match_score, reverse=True)
            matched_jobs = matched_jobs[:max_jobs]  # Top matches
            
            results['jobs_matched'] = len(matched_jobs)
            
            # If still no matches, use top jobs anyway (for testing)
            if not matched_jobs and jobs:
                matched_jobs = jobs[:max_jobs]
                for job in matched_jobs:
                    job.match_score = 0.5  # Default score
                results['jobs_matched'] = len(matched_jobs)
            
            # Generate cover letters
            print(f"[AUTO AGENT] Generating cover letters for {len(matched_jobs)} matched jobs...")
            for job in matched_jobs:
                try:
                    cover_letter = self.cover_letter_gen.generate_cover_letter(job)
                    job.cover_letter = cover_letter
                    results['cover_letters_generated'] += 1
                except Exception as e:
                    print(f"[ERROR] Failed to generate cover letter: {e}")
            
            # Auto-apply if enabled
            if auto_apply:
                print(f"[AUTO AGENT] Auto-applying to {len(matched_jobs)} jobs...")
                for job in matched_jobs:
                    try:
                        # Skip search URL jobs - only apply to actual job postings
                        if hasattr(job, 'source') and 'search-url' in job.source.lower():
                            print(f"[AUTO AGENT] Skipping search URL job: {job.title}")
                            continue
                        
                        # Use submit_application which handles auto-apply
                        result = self.application_automator.submit_application(
                            job, 
                            auto_submit=True  # Enable auto-submit
                        )
                        if result.get('success') or result.get('status') == 'pending_user_action':
                            results['applications_sent'] += 1
                        time.sleep(2)  # Rate limiting
                    except Exception as e:
                        print(f"[ERROR] Failed to apply to {job.title}: {e}")
                        import traceback
                        traceback.print_exc()
            
            # Store actual JobListing objects (not dicts) for the jobs page
            results['jobs'] = matched_jobs  # Keep as JobListing objects
            
        except Exception as e:
            print(f"[ERROR] Auto search failed: {e}")
            results['error'] = str(e)
        
        return results
