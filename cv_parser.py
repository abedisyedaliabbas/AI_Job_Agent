"""
CV Parser - Extracts data from CV text/PDF
Based on the provided CV data for Syed Ali Abbas Abedi
"""
import json
from profile_manager import ProfileManager, Education, Experience, Publication, Skill


def parse_abedi_cv() -> dict:
    """
    Parse the CV data for Syed Ali Abbas Abedi
    This function extracts structured data from the CV
    """
    cv_data = {
        "name": "Syed Ali Abbas Abedi",
        "email": "abedisyedaliabbas@gmail.com",
        "phone": "+65 8923 4027",
        "location": "Singapore",
        "date_of_birth": "04/06/1994",
        "website": "https://abedisyedaliabbas.github.io/abedi-research/",
        "orcid": "0000-0001-6131-5039",
        "education": [
            {
                "degree": "PhD",
                "institution": "Singapore University of Technology and Design (SUTD)",
                "field": "Science, Mathematics & Technology",
                "graduation_date": "30/06/2024",
                "thesis": "Computational Design and Mechanistic Investigation of Fluorophores Based on Excited-State Conformational Dynamics"
            },
            {
                "degree": "MS",
                "institution": "Lahore University of Management Sciences",
                "field": "Mathematics",
                "graduation_date": "30/06/2019",
                "thesis": "Predator-Prey Model with Age Structures"
            },
            {
                "degree": "BSc",
                "institution": "University of Engineering & Technology, Lahore",
                "field": "Chemical Engineering and Technology",
                "graduation_date": "31/01/2016"
            }
        ],
        "experience": [
            {
                "title": "Visiting Researcher",
                "company": "Nanyang Technological University (NTU)",
                "location": "Singapore",
                "start_date": "01/09/2025",
                "end_date": "Present",
                "description": [
                    "Actively collaborating with NTU faculty to establish the data pipeline necessary for the AI-Guided Photostability project",
                    "Utilising the HPC facilities for preliminary large-scale Density Functional Theory (DFT) calculations on novel fluorophore libraries"
                ]
            },
            {
                "title": "Postdoctoral Research Fellow",
                "company": "Singapore University of Technology and Design (SUTD)",
                "location": "Singapore",
                "start_date": "23/09/2024",
                "end_date": "Present",
                "description": [
                    "Perform advanced excited-state calculations to model, design, and elucidate the photophysical properties of organic fluorophores",
                    "Leverage machine-learning algorithms to predict key molecular properties and accelerate the design of next-generation fluorophore systems"
                ]
            },
            {
                "title": "Visiting Researcher",
                "company": "University College London & Queen Mary University of London",
                "location": "UK",
                "start_date": "03/04/2023",
                "end_date": "31/07/2023",
                "description": [
                    "Led a computational research project to model excited state dynamics of organic molecules, focusing on the environmental effects in the condensed phase",
                    "Employed Gaussian and advanced methods like CASSCF and CASPT2 for accurate dynamic correlation computations",
                    "Conducted non-adiabatic dynamics simulations to explore decay mechanisms"
                ]
            },
            {
                "title": "Mentor, SHARP Undergraduate Research Program",
                "company": "SUTD",
                "location": "Singapore",
                "start_date": "01/09/2022",
                "end_date": "30/06/2024",
                "description": [
                    "Guided undergraduates through independent computational photophysics projects",
                    "Organized bi-weekly coding workshops in Python for quantum-chemistry automation"
                ]
            }
        ],
        "skills": [
            {
                "category": "Computational Chemistry & Photophysics",
                "skills": [
                    "Quantum Chemistry: DFT, TD-DFT, CASSCF/CASPT2",
                    "Non-Adiabatic Dynamics",
                    "MD Simulations",
                    "Gaussian, ORCA, OpenMolcas, Avogadro, GAMESS"
                ]
            },
            {
                "category": "Data Science & Machine Learning (AI-for-X)",
                "skills": [
                    "Python (Pandas, NumPy, Matplotlib)",
                    "Scikit-learn, PyTorch",
                    "Data Curation",
                    "Feature Engineering",
                    "Regression"
                ]
            },
            {
                "category": "Programming & Data Processing",
                "skills": [
                    "Python",
                    "Bash Scripting",
                    "High-Performance Computing (HPC)",
                    "PBS Workload Managers",
                    "Git/GitHub"
                ]
            },
            {
                "category": "Molecular Design & Modeling",
                "skills": [
                    "Fluorophore Design",
                    "Excited-State Dynamics",
                    "Structure-Property Relationship Mapping",
                    "TICT/PET/ESIPT Mechanism Elucidation"
                ]
            }
        ],
        "publications": [
            {
                "title": "Hetero-Hydrazone Photoswitches",
                "authors": "D. Sosnin, Syed Ali Abbas Abedi, M. Izadyar, Y. Ünal, X. Liu, I. Aprahamian",
                "journal": "Angew. Chem. Int. Ed.",
                "year": 2025,
                "doi": "10.1002/anie.202515136"
            },
            {
                "title": "\"Clicked\" Hydrazone Photoswitches",
                "authors": "D. Sosnin, M. Izadyar, Syed Ali Abbas Abedi, X. Liu, I. Aprahamian",
                "journal": "J. Am. Chem. Soc.",
                "year": 2025,
                "doi": "10.1021/jacs.5c02183"
            },
            {
                "title": "Unveiling the Power of Dark State Photocages: An Efficient Pathway to Triplet State under NIR Irradiation",
                "authors": "Q. Hu, J. Du, Syed Ali Abbas Abedi, X. Liu, S. Long, W. Sun, J. Fan, X. Peng",
                "journal": "Angew. Chem. Int. Ed.",
                "year": 2025,
                "doi": "10.1002/ange.202504670"
            },
            {
                "title": "Super-Photostable Organic Dye for Long-Term Live-Cell Single-Protein Imaging",
                "authors": "D. H. Kim, H. M. Triet, S. H. Lee, S. Jazani, S. Jang, Syed Ali Abbas Abedi, X. Liu, J. Seo, T. Ha, Y. T. Chang, S. H. Ryu",
                "journal": "Nature Methods",
                "year": 2025,
                "doi": "10.1038/s41592-024-02584-0"
            },
            {
                "title": "Oxazolidine-Caged Heptamethine Cyanine Switch Exhibits High Photostability for Bioimaging via Buffering Fluorogenicity",
                "authors": "Q. Qi, J. Li, Q. Qiao, C. Yan, M. Izadyar, C. Wang, Syed Ali Abbas Abedi, X. Liu, Z. Guo, et al.",
                "journal": "CCS Chemistry",
                "year": 2025
            },
            {
                "title": "Moisture-Tolerant, Thermally Stable and Light-Switchable Adhesive Platform Based on Reversible Redshifted [2+2] Photocycloaddition",
                "authors": "X. Y. Oh, Q. V. Thi, M. M. L. Yu, M. Izadyar, Syed Ali Abbas Abedi, X. Liu, V. X. Truong",
                "journal": "Adv. Funct. Mater.",
                "year": 2025
            },
            {
                "title": "Highly Stable Electrofluorochromic Switching of AIE-Active Conjugated Polymers",
                "authors": "R. Tao, B. Y. K. Hui, K. L. O. Chin, X. Y. D. Soo, D. Zhang, Syed Ali Abbas Abedi, P. Bi, X. Liu, et al.",
                "journal": "Mater. Chem. Front.",
                "year": 2025
            },
            {
                "title": "\"Superimposed\" Spectral Characteristics of Fluorophores Arising from Cross-Conjugation Hybridization",
                "authors": "K. An, Q. Qiao, Syed Ali Abbas Abedi, X. Liu, Z. Xu",
                "journal": "Chin. Chem. Lett.",
                "year": 2025,
                "doi": "10.1016/j.cclet.2024.109786"
            },
            {
                "title": "Conformational Folding Activates Photoinduced Electron Transfer",
                "authors": "S. Huang, Syed Ali Abbas Abedi, Z. Li, R. Huang, X. Yan, M. Izadyar, Q. Qiao, Y. Fang, Z. Xu, X. Liu",
                "journal": "CCS Chemistry",
                "year": 2024,
                "doi": "10.31635/ccschem.024.202404541",
                "co_first": True
            },
            {
                "title": "Solvatochromic Fluorescent Ethynyl Naphthalimide Derivatives for Detection of Water in Organic Solvents",
                "authors": "Q. P. N. Nhu, Syed Ali Abbas Abedi, S. Chanmungkalakul, M. Sukwattanasinitt, Y.-T. Chang, P. Rashatasakhon",
                "journal": "Dyes Pigments",
                "year": 2024,
                "doi": "10.1016/j.dyepig.2024.112188"
            },
            {
                "title": "The Dark Side of Cyclooctatetraene (COT): Photophysics in the Singlet States of \"Self-Healing\" Dyes",
                "authors": "S. Chanmungkalakul, Syed Ali Abbas Abedi, F. J. Hernández, J. Xu, X. Liu",
                "journal": "Chin. Chem. Lett.",
                "year": 2024,
                "doi": "10.1016/j.cclet.2023.109227",
                "co_first": True
            },
            {
                "title": "Aryl-Modified Pentamethyl Cyanine Dyes at the C2' Position: A Tunable Platform for Activatable Photosensitizers",
                "authors": "F. Han, Syed Ali Abbas Abedi, S. He, H. Zhang, S. Long, X. Zhou, S. Chanmungkalakul, H. Ma, W. Sun, X. Liu, J. Du, J. Fan, X. Peng",
                "journal": "Adv. Sci.",
                "year": 2023,
                "doi": "10.1002/advs.202305761",
                "co_first": True
            },
            {
                "title": "Janus-Type ESIPT Chromophores with Distinctive Intramolecular Hydrogen-Bonding Selectivity",
                "authors": "Y. Chen, S. Lu, Syed Ali Abbas Abedi, M. Jeong, H. Li, M. H. Kim, S. Park, X. Liu, J. Yoon, X. Chen",
                "journal": "Angew. Chem. Int. Ed.",
                "year": 2023,
                "doi": "10.1002/anie.202311543",
                "co_first": True
            },
            {
                "title": "Blending Low-Frequency Vibrations and Push-Pull Effects Affords Superior Photoacoustic Imaging Agents",
                "authors": "L. Yu, Syed Ali Abbas Abedi, J. Lee, Y. Xu, S. Son, W. Chi, M. Li, X. Liu, J. H. Park, J. S. Kim",
                "journal": "Angew. Chem. Int. Ed.",
                "year": 2023,
                "doi": "10.1002/anie.202307797",
                "co_first": True
            },
            {
                "title": "Rational Design and Application of an Indolium-Derived Heptamethine Cyanine with Record-Long NIR-II Emission",
                "authors": "X. Ma, Y. Huang, Syed Ali Abbas Abedi, H. Kim, T. T. B. Davin, X. Liu, W. C. Yang, Y. Sun, S. H. Liu, J. Yin, J. Yoon, G. F. Yang",
                "journal": "CCS Chemistry",
                "year": 2022,
                "doi": "10.31635/ccschem.021.202101630"
            },
            {
                "title": "A PET-Based Fluorescent Probe for Monitoring Labile Fe(II) Pools in Macrophage Activations and Ferroptosis",
                "authors": "W. Xing, H. Xu, H. Ma, Syed Ali Abbas Abedi, S. Wang, X. Zhang, X. Liu, H. Xu, W. Wang, K. Lou",
                "journal": "Chem. Commun.",
                "year": 2022,
                "doi": "10.1039/D1CC06611K"
            },
            {
                "title": "Restriction of Twisted Intramolecular Charge Transfer Enables the Aggregation-Induced Emission of 1-(N,N-Dialkylamino)-naphthalene Derivatives",
                "authors": "Syed Ali Abbas Abedi, W. Chi, D. Tan, T. Shen, C. Wang, E. C. Ang, C. H. Tan, F. Anariba, X. Liu",
                "journal": "J. Phys. Chem. A",
                "year": 2021,
                "doi": "10.1021/acs.jpca.1c06263"
            },
            {
                "title": "Fluorescence Umpolung Enables Light-Up Sensing of N-Acetyltransferases and Nerve Agents",
                "authors": "C. Yan, Z. Guo, W. Chi, W. Fu, Syed Ali Abbas Abedi, X. Liu, H. Tian, W. Zhu",
                "journal": "Nat. Commun.",
                "year": 2021,
                "doi": "10.1038/s41467-021-24187-5"
            },
            {
                "title": "A Computational Protocol for Uncovering Photoinduced Electron Transfer Mechanisms in Fluorescent Molecules",
                "authors": "Syed Ali Abbas Abedi, Lovelesh Lovelesh, Weijie Chi, Xiaogang Liu",
                "journal": "Nature Protocols",
                "year": 2025,
                "status": "revised submission",
                "manuscript": "NP-PI250180"
            },
            {
                "title": "Red and Robust: Highly Stable Electrofluorochromic Switching in Cyano-Substituted Aggregation-Induced Emission-Active Conjugated Polymers",
                "authors": "Bryan Yat Kit Hui, Ran Tao, Kang Le Osmund Chin, Xiang Yun Debbie Soo, Syed Ali Abbas Abedi, Kok Chan Chong, Xiaogang Liu, Jianwei Xu, Ming Hui Chua",
                "journal": "Advanced Optical Materials",
                "year": 2025,
                "status": "revised submission",
                "manuscript": "adom.202502075R1"
            },
            {
                "title": "Barrierless Conical Intersection as a Photophysical Design Principle for Photoacoustic and Photothermal Contrast Agents",
                "authors": "Zhimin Wu, Syed Ali Abbas Abedi, Rongrong Huang, Lili Lin, Xiaogang Liu",
                "journal": "Chinese Chemical Letters",
                "year": 2025,
                "status": "under review",
                "manuscript": "CCLET-D-25 03690"
            },
            {
                "title": "A General Strategy Towards Multicolor Fluorogenic Peptides for Wash-Free Bioassays",
                "authors": "Man Sing Wong, Lorena Mendive-Tapia, Utsa Karmakar, Lovelesh Vashist, Zandile Nare, Karolina Tokarczyk, Kohei Iijima, Kazuya Kikuchi, Syed Ali Abbas Abedi, Xiaogang Liu, Marc Vendrell",
                "journal": "Nature Chemistry",
                "year": 2025,
                "status": "under revision",
                "manuscript": "NCHEM-25051513"
            },
            {
                "title": "Solvent-Controlled Gsipt and Tict in a Schiff Base",
                "authors": "Syed Ali Abbas Abedi, P. Yadav, Xiaogang Liu",
                "journal": "SSRN Preprint",
                "year": 2023,
                "doi": "10.2139/ssrn.4563845"
            },
            {
                "title": "Computational Design and Mechanistic Investigation of Fluorophores Based on Excited-State Conformational Dynamics",
                "authors": "Syed Ali Abbas Abedi",
                "journal": "Doctoral Dissertation",
                "year": 2024,
                "institution": "Singapore University of Technology and Design (SUTD)",
                "supervisor": "Prof. Xiaogang Liu"
            }
        ],
        "awards": [
            "2024: Awarded bursary from EPSRC Catalysis Hub and RSC Summer School in Catalysis up to £1000",
            "2023: Honored with the APC Exhibitor Prize, 12th Asian Photochemistry Conference - Awarded up to $250",
            "2023: Received Emerging Area in Photochemistry research grant, 12th Asian Photochemistry Conference - Funded up to $1,000",
            "2022: Awarded the RSC Travel Grant for Researchers by the Royal Society of Chemistry - Supported travel expenses up to £500",
            "2022: Granted funding from the American Institute of Chemical Engineers (AIChE) for attending the Quantum Computing Workshop at Denmark Technical Institute (DTU) - Up to $900",
            "2020-2024: PhD SUTD Fellowship - Scholarship covering doctoral studies"
        ],
        "presentations": [
            "Participated @ Global Young Scientists Summit in Singapore (2025)",
            "Invited speaker @ Interdisciplinary Medicine Young Scholars Forum on Biomedical Applications of Molecular Probes, Singapore (2024)",
            "Participated @ 12th Singapore International Chemistry Conference (2024)",
            "Poster @ Catalysis Fundamentals and Practice Summer School, Liverpool, UK (2024)",
            "Oral speaker @ The 5th International Conference on Fluorescent Biomolecules, Hong Kong (2024)",
            "Poster @ The 12th Asian Photochemistry Conference, Melbourne, Australia (2023)",
            "Poster @ 7th Green and Sustainable Chemistry Conference, Dresden, Germany (2023)",
            "Participated @ Global Young Scientists Summit in Singapore (2023)",
            "Poster @ 3rd Commonwealth Chemistry Posters Event, Online (2022)",
            "Oral speaker @ 7th International Symposium of Quantum Beam Science at Ibaraki University, Japan (2022)",
            "Oral speaker @ Quantum Computing Applications in Chemical and Biochemical Engineering Workshop, Copenhagen, Denmark (2022)"
        ],
        "metrics": {
            "total_citations": 419,
            "h_index": 9,
            "i10_index": 9,
            "researcher_id": "GYD-7870-2022"
        },
        "research_interests": [
            "Computational Chemistry",
            "Quantum Chemistry",
            "Photophysics",
            "Machine Learning for Molecular Design",
            "AI-for-Science",
            "Excited-State Dynamics",
            "Fluorophore Design",
            "Molecular Modeling"
        ],
        "research_summary": "I'm a computational chemist working at the intersection of artificial intelligence and molecular design. My research focuses on understanding and designing photostable organic materials using quantum chemical methods and machine learning approaches."
    }
    
    return cv_data


if __name__ == "__main__":
    # Parse CV and create profile
    parser = ProfileManager()
    cv_data = parse_abedi_cv()
    profile = parser.load_from_cv_data(cv_data)
    parser.save_to_file()
    print(f"Profile created for {profile.name}")
    print(f"Saved to {parser.profile_file}")
