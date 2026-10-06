import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from students.models import Branch, AcademicYear, Skill, Interest, StudentProfile, StudentSkill, Notification
from opportunities.models import Opportunity, SavedOpportunity, Application
from matching.services import run_matching_engine_for_student


class Command(BaseCommand):
    help = 'Seeds database with realistic demo data: 30+ students, 50+ skills, 30+ interests, 40+ opportunities'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE("Beginning database seeding for OpportunityMatch..."))

        # 1. Superuser
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@opportunitymatch.edu',
                'first_name': 'Platform',
                'last_name': 'Administrator',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS("Created admin user: admin / admin123"))

        # 2. Academic Years
        year_data = [
            (1, '1st Year'),
            (2, '2nd Year'),
            (3, '3rd Year'),
            (4, '4th Year'),
            (5, 'Postgraduate / PhD'),
        ]
        years = {}
        for num, name in year_data:
            obj, _ = AcademicYear.objects.get_or_create(year_number=num, defaults={'name': name})
            years[num] = obj

        # 3. Branches
        branch_data = [
            ('Computer Science and Engineering', 'CSE'),
            ('Information Technology', 'IT'),
            ('Electronics and Communication Engineering', 'ECE'),
            ('Electrical and Electronics Engineering', 'EEE'),
            ('Artificial Intelligence and Data Science', 'AI&DS'),
            ('Mechanical Engineering', 'ME'),
            ('Civil Engineering', 'CE'),
            ('Computer Science and Business Systems', 'CSBS'),
        ]
        branches = {}
        for name, code in branch_data:
            obj, _ = Branch.objects.get_or_create(code=code, defaults={'name': name})
            branches[code] = obj

        # 4. 50+ Skills
        skills_catalog = [
            # Programming Languages
            ('Python', 'Programming Languages', 'High-level general-purpose programming language.'),
            ('Java', 'Programming Languages', 'Object-oriented language for enterprise applications.'),
            ('C++', 'Programming Languages', 'High-performance compiled language.'),
            ('JavaScript', 'Programming Languages', 'Dynamic scripting language for web and node ecosystems.'),
            ('TypeScript', 'Programming Languages', 'Typed superset of JavaScript.'),
            ('Go', 'Programming Languages', 'Statically typed compiled language designed at Google.'),
            ('Rust', 'Programming Languages', 'Systems programming language focused on safety and concurrency.'),
            ('Kotlin', 'Programming Languages', 'Modern statically typed language for Android.'),
            ('Swift', 'Programming Languages', 'Apple ecosystem compiled language.'),
            ('C#', 'Programming Languages', 'Object-oriented language for .NET framework.'),
            # Web & Mobile Frameworks
            ('Django', 'Web & Mobile Development', 'High-level Python web framework.'),
            ('React', 'Web & Mobile Development', 'Component-based frontend JavaScript library.'),
            ('Node.js', 'Web & Mobile Development', 'Asynchronous event-driven JavaScript runtime.'),
            ('FastAPI', 'Web & Mobile Development', 'Modern, fast web framework for building APIs with Python.'),
            ('Next.js', 'Web & Mobile Development', 'The React Framework for the Web.'),
            ('Spring Boot', 'Web & Mobile Development', 'Java-based framework for microservices.'),
            ('Flutter', 'Web & Mobile Development', 'Google multi-platform UI toolkit.'),
            ('HTML5/CSS3', 'Web & Mobile Development', 'Core frontend web markup and styling standards.'),
            ('Express.js', 'Web & Mobile Development', 'Minimalist web framework for Node.js.'),
            ('GraphQL', 'Web & Mobile Development', 'Query language for APIs.'),
            # AI & Data Science
            ('Machine Learning', 'AI & Data Science', 'Algorithms that improve automatically through experience.'),
            ('Deep Learning', 'AI & Data Science', 'Neural networks with multiple representation layers.'),
            ('PyTorch', 'AI & Data Science', 'Open source machine learning framework.'),
            ('TensorFlow', 'AI & Data Science', 'End-to-end open source platform for machine learning.'),
            ('Scikit-Learn', 'AI & Data Science', 'Machine learning in Python for classification and regression.'),
            ('Pandas', 'AI & Data Science', 'Data manipulation and analysis library for Python.'),
            ('NumPy', 'AI & Data Science', 'Fundamental package for scientific computing with Python.'),
            ('Computer Vision', 'AI & Data Science', 'Visual pattern processing and image understanding.'),
            ('Natural Language Processing', 'AI & Data Science', 'Text analysis, transformers, and LLM fine-tuning.'),
            ('Data Analysis', 'AI & Data Science', 'Inspecting, cleansing, and modeling data.'),
            # Databases
            ('SQL', 'Databases', 'Domain-specific language used in programming relational databases.'),
            ('PostgreSQL', 'Databases', 'Powerful, open-source object-relational database system.'),
            ('MongoDB', 'Databases', 'Document-oriented NoSQL database program.'),
            ('Redis', 'Databases', 'In-memory data structure store used as a database and cache.'),
            ('MySQL', 'Databases', 'Open-source relational database management system.'),
            # Cloud & DevOps
            ('Docker', 'Cloud & DevOps', 'Platform designed to build, share, and run container applications.'),
            ('Kubernetes', 'Cloud & DevOps', 'Automated container orchestration system.'),
            ('AWS', 'Cloud & DevOps', 'Amazon Web Services cloud computing platform.'),
            ('Google Cloud Platform', 'Cloud & DevOps', 'Google suite of cloud computing services.'),
            ('Microsoft Azure', 'Cloud & DevOps', 'Microsoft cloud computing platform.'),
            ('CI/CD Pipelines', 'Cloud & DevOps', 'Continuous integration and continuous deployment pipelines.'),
            ('Linux Administration', 'Cloud & DevOps', 'Command line and system management in Linux/UNIX.'),
            ('Terraform', 'Cloud & DevOps', 'Infrastructure as Code software tool.'),
            # Tools & Methodologies
            ('Git', 'Tools & Methodologies', 'Distributed version control system.'),
            ('Data Structures & Algorithms', 'Tools & Methodologies', 'Foundational CS data representation and algorithmic techniques.'),
            ('RESTful APIs', 'Tools & Methodologies', 'Architectural style for network-based hypermedia systems.'),
            ('System Design', 'Tools & Methodologies', 'Designing large-scale scalable architectures.'),
            ('Unit Testing', 'Tools & Methodologies', 'Software testing method to verify individual units.'),
            ('Agile / Scrum', 'Tools & Methodologies', 'Iterative software development lifecycle.'),
            ('Postman', 'Tools & Methodologies', 'API platform for building and using APIs.'),
            # Cybersecurity & Design
            ('Cybersecurity', 'Cybersecurity', 'Techniques for securing computer systems and networks.'),
            ('Ethical Hacking', 'Cybersecurity', 'Authorized penetration testing and vulnerability analysis.'),
            ('UI/UX Design', 'UI/UX Design', 'User interface and interaction experience design.'),
            ('Figma', 'UI/UX Design', 'Collaborative web application for interface design.'),
        ]

        skills = {}
        for name, category, desc in skills_catalog:
            obj, _ = Skill.objects.get_or_create(name=name, defaults={'category': category, 'description': desc})
            skills[name] = obj

        # 5. 30+ Interests
        interests_catalog = [
            'Artificial Intelligence', 'Machine Learning', 'Web Development', 'Cloud Computing',
            'Cybersecurity', 'Data Science', 'IoT (Internet of Things)', 'Blockchain & Web3',
            'Mobile App Development', 'Quantum Computing', 'DevOps & SRE', 'Robotics & Automation',
            'Bioinformatics', 'Natural Language Processing', 'Computer Vision', 'Autonomous Systems',
            'Open Source Software', 'Distributed Systems', 'FinTech', 'HealthTech',
            'EdTech', 'UI/UX Design', 'Competitive Programming', 'Game Development',
            'AR/VR & Metaverse', 'Big Data Engineering', 'Green Computing', 'Database Systems',
            'Network Security', 'API & Microservices Architecture'
        ]
        interests = {}
        for name in interests_catalog:
            obj, _ = Interest.objects.get_or_create(name=name, defaults={'description': f'Focus on {name}'})
            interests[name] = obj

        # 6. 40+ Opportunities across all 9 categories
        opp_data = [
            # Internships
            {
                'title': 'AI/ML Research Engineering Internship',
                'organization': 'Apex Neural Labs',
                'description': 'Work alongside senior research scientists developing cutting-edge foundation models, vision transformers, and multimodal AI pipelines.',
                'type': 'Internship', 'domain': 'Artificial Intelligence', 'loc': 'Remote', 'mode': 'Online',
                'dur': '3 Months', 'cgpa': 7.5, 'days': 35, 'url': 'https://example.com/apply/apex-ai',
                'branches': ['CSE', 'IT', 'AI&DS'], 'years': [3, 4, 5],
                'req_skills': ['Python', 'Machine Learning', 'PyTorch', 'SQL', 'Git'],
                'interests': ['Artificial Intelligence', 'Machine Learning', 'Data Science'],
            },
            {
                'title': 'Full-Stack Web Development Internship',
                'organization': 'Nexus Cloud Systems',
                'description': 'Design and implement scalable REST APIs and reactive dashboard interfaces for cloud telemetry and infrastructure monitoring.',
                'type': 'Internship', 'domain': 'Web Development', 'loc': 'Bangalore', 'mode': 'Hybrid',
                'dur': '6 Months', 'cgpa': 7.0, 'days': 25, 'url': 'https://example.com/apply/nexus-web',
                'branches': ['CSE', 'IT', 'ECE'], 'years': [3, 4],
                'req_skills': ['Python', 'Django', 'React', 'SQL', 'Git', 'Docker'],
                'interests': ['Web Development', 'Cloud Computing', 'API & Microservices Architecture'],
            },
            {
                'title': 'Cloud Infrastructure & DevOps Internship',
                'organization': 'Vertex Global Infrastructure',
                'description': 'Automate multi-region AWS infrastructure deployment using Terraform, Kubernetes, and continuous delivery pipelines.',
                'type': 'Internship', 'domain': 'Cloud Computing', 'loc': 'Remote', 'mode': 'Online',
                'dur': '3 Months', 'cgpa': 7.0, 'days': 20, 'url': 'https://example.com/apply/vertex-devops',
                'branches': ['CSE', 'IT', 'ECE'], 'years': [2, 3, 4],
                'req_skills': ['Docker', 'Kubernetes', 'AWS', 'Linux Administration', 'Git'],
                'interests': ['Cloud Computing', 'DevOps & SRE', 'Distributed Systems'],
            },
            {
                'title': 'Cybersecurity Penetration Testing Internship',
                'organization': 'CyberShield Defense Corp',
                'description': 'Perform vulnerability scanning, penetration tests, and security audits across web applications and network nodes.',
                'type': 'Internship', 'domain': 'Cybersecurity', 'loc': 'Hyderabad', 'mode': 'Offline',
                'dur': '3 Months', 'cgpa': 7.2, 'days': 18, 'url': 'https://example.com/apply/cybershield',
                'branches': ['CSE', 'IT'], 'years': [3, 4],
                'req_skills': ['Cybersecurity', 'Ethical Hacking', 'Linux Administration', 'Python'],
                'interests': ['Cybersecurity', 'Network Security'],
            },
            {
                'title': 'Data Science & Analytics Internship',
                'organization': 'DataVibe Analytics',
                'description': 'Extract actionable customer insights and build predictive churn models using statistical modeling and exploratory data analysis.',
                'type': 'Internship', 'domain': 'Data Science', 'loc': 'Remote', 'mode': 'Online',
                'dur': '2 Months', 'cgpa': 7.0, 'days': 30, 'url': 'https://example.com/apply/datavibe',
                'branches': ['CSE', 'IT', 'AI&DS'], 'years': [2, 3, 4],
                'req_skills': ['Python', 'Pandas', 'SQL', 'Data Analysis', 'Scikit-Learn'],
                'interests': ['Data Science', 'Machine Learning'],
            },
            {
                'title': 'Embedded Systems & IoT Engineering Internship',
                'organization': 'AeroSens Robotics',
                'description': 'Develop low-power sensor firmware and wireless communication drivers for industrial IoT and smart telematics units.',
                'type': 'Internship', 'domain': 'IoT (Internet of Things)', 'loc': 'Pune', 'mode': 'Offline',
                'dur': '4 Months', 'cgpa': 6.8, 'days': 22, 'url': 'https://example.com/apply/aerosens',
                'branches': ['ECE', 'EEE', 'ME'], 'years': [3, 4],
                'req_skills': ['C++', 'Linux Administration', 'Data Structures & Algorithms'],
                'interests': ['IoT (Internet of Things)', 'Robotics & Automation'],
            },
            {
                'title': 'Mobile Application Development Internship (Flutter)',
                'organization': 'PulseWave Mobile',
                'description': 'Build sleek cross-platform applications for iOS and Android with smooth 60fps animations and offline sync capabilities.',
                'type': 'Internship', 'domain': 'Mobile App Development', 'loc': 'Remote', 'mode': 'Online',
                'dur': '3 Months', 'cgpa': 6.5, 'days': 28, 'url': 'https://example.com/apply/pulsewave',
                'branches': ['CSE', 'IT', 'CSBS'], 'years': [2, 3, 4],
                'req_skills': ['Flutter', 'RESTful APIs', 'Git', 'UI/UX Design'],
                'interests': ['Mobile App Development', 'UI/UX Design'],
            },
            {
                'title': 'FinTech Backend Engineering Internship',
                'organization': 'Zenith Capital Tech',
                'description': 'Implement high-throughput transaction processing microservices with PostgreSQL, Redis cache layers, and strict ACID guarantees.',
                'type': 'Internship', 'domain': 'FinTech', 'loc': 'Mumbai', 'mode': 'Hybrid',
                'dur': '6 Months', 'cgpa': 7.8, 'days': 15, 'url': 'https://example.com/apply/zenith',
                'branches': ['CSE', 'IT'], 'years': [3, 4],
                'req_skills': ['Java', 'Spring Boot', 'SQL', 'PostgreSQL', 'Docker', 'System Design'],
                'interests': ['FinTech', 'Distributed Systems', 'Database Systems'],
            },

            # Hackathons
            {
                'title': 'Global AI Hackathon 2026',
                'organization': 'Open AI Collective',
                'description': 'A 48-hour global hackathon challenging student developers to solve real-world sustainability and accessibility problems using multimodal AI.',
                'type': 'Hackathon', 'domain': 'Artificial Intelligence', 'loc': 'Virtual / Global', 'mode': 'Online',
                'dur': '3 Days', 'cgpa': 0.0, 'days': 14, 'url': 'https://example.com/hackathons/global-ai',
                'branches': [], 'years': [],
                'req_skills': ['Python', 'Machine Learning', 'Git', 'RESTful APIs'],
                'interests': ['Artificial Intelligence', 'Machine Learning', 'Open Source Software'],
            },
            {
                'title': 'Smart City Sustainable IoT Hackathon',
                'organization': 'UrbanFuture Foundation',
                'description': 'Propose and prototype intelligent smart-city solutions focusing on clean energy distribution and intelligent traffic coordination.',
                'type': 'Hackathon', 'domain': 'IoT (Internet of Things)', 'loc': 'Delhi', 'mode': 'Hybrid',
                'dur': '2 Days', 'cgpa': 0.0, 'days': 12, 'url': 'https://example.com/hackathons/smartcity',
                'branches': ['CSE', 'ECE', 'EEE', 'CE', 'ME'], 'years': [1, 2, 3, 4],
                'req_skills': ['Python', 'C++', 'Data Structures & Algorithms'],
                'interests': ['IoT (Internet of Things)', 'Autonomous Systems', 'Green Computing'],
            },
            {
                'title': 'Web3 & Decentralized Identity Hackathon',
                'organization': 'ChainMatrix Alliance',
                'description': 'Build decentralized apps and privacy-preserving self-sovereign identity verification modules using cryptographic zero-knowledge proofs.',
                'type': 'Hackathon', 'domain': 'Blockchain & Web3', 'loc': 'Virtual', 'mode': 'Online',
                'dur': '4 Days', 'cgpa': 0.0, 'days': 21, 'url': 'https://example.com/hackathons/web3-identity',
                'branches': ['CSE', 'IT'], 'years': [2, 3, 4],
                'req_skills': ['JavaScript', 'TypeScript', 'React', 'Git'],
                'interests': ['Blockchain & Web3', 'Cybersecurity'],
            },
            {
                'title': 'HealthTech Rapid Innovation Sprint',
                'organization': 'MedLife Innovators',
                'description': 'Create intuitive patient-doctor monitoring dashboards, remote diagnostic triage bots, and biomedical data visualization tools.',
                'type': 'Hackathon', 'domain': 'HealthTech', 'loc': 'Bangalore', 'mode': 'Offline',
                'dur': '3 Days', 'cgpa': 6.0, 'days': 16, 'url': 'https://example.com/hackathons/healthtech-sprint',
                'branches': ['CSE', 'IT', 'AI&DS'], 'years': [2, 3, 4],
                'req_skills': ['Python', 'React', 'UI/UX Design', 'SQL'],
                'interests': ['HealthTech', 'Web Development', 'UI/UX Design'],
            },

            # Scholarships
            {
                'title': 'NextGen STEM Excellence Scholarship 2026',
                'organization': 'Horizon Educational Trust',
                'description': 'Merit-based scholarship providing full tuition assistance and mentor matching for undergraduate engineering students with proven technical aptitude.',
                'type': 'Scholarship', 'domain': 'Core Engineering', 'loc': 'National', 'mode': 'Online',
                'dur': '1 Year', 'cgpa': 8.0, 'days': 40, 'url': 'https://example.com/scholarships/nextgen-stem',
                'branches': ['CSE', 'IT', 'ECE', 'EEE', 'ME', 'CE', 'AI&DS'], 'years': [2, 3, 4],
                'req_skills': ['Data Structures & Algorithms'],
                'interests': ['Artificial Intelligence', 'Web Development', 'Cloud Computing'],
            },
            {
                'title': 'Women in Technology Leadership Scholarship',
                'organization': 'Ada Lovelace Tech Foundation',
                'description': 'Financial support and executive leadership mentorship for female and underrepresented students pursuing computer science and computing careers.',
                'type': 'Scholarship', 'domain': 'Computer Science', 'loc': 'Global', 'mode': 'Online',
                'dur': 'Academic Year', 'cgpa': 7.5, 'days': 45, 'url': 'https://example.com/scholarships/women-in-tech',
                'branches': ['CSE', 'IT', 'AI&DS', 'CSBS'], 'years': [2, 3, 4],
                'req_skills': ['Python', 'Git'],
                'interests': ['Artificial Intelligence', 'Web Development', 'Open Source Software'],
            },
            {
                'title': 'Future Leaders Cloud & Data Scholarship',
                'organization': 'CloudScale Consortium',
                'description': 'Covers certification voucher costs, cloud computing credits, and direct stipend awards for high-achieving data and systems students.',
                'type': 'Scholarship', 'domain': 'Cloud Computing', 'loc': 'Online', 'mode': 'Online',
                'dur': '6 Months', 'cgpa': 8.2, 'days': 32, 'url': 'https://example.com/scholarships/future-leaders-cloud',
                'branches': ['CSE', 'IT', 'AI&DS'], 'years': [3, 4],
                'req_skills': ['AWS', 'Docker', 'SQL'],
                'interests': ['Cloud Computing', 'Data Science'],
            },

            # Research Opportunities
            {
                'title': 'Multimodal LLM Interpretability Research Fellowship',
                'organization': 'Institute for Advanced AI Studies',
                'description': 'Undergraduate and postgraduate research fellowship examining mechanistic interpretability and attention distribution in transformer language models.',
                'type': 'Research', 'domain': 'Artificial Intelligence', 'loc': 'Remote', 'mode': 'Online',
                'dur': '4 Months', 'cgpa': 8.0, 'days': 29, 'url': 'https://example.com/research/llm-interpretability',
                'branches': ['CSE', 'IT', 'AI&DS'], 'years': [3, 4, 5],
                'req_skills': ['Python', 'PyTorch', 'Natural Language Processing', 'Machine Learning', 'Git'],
                'interests': ['Artificial Intelligence', 'Natural Language Processing', 'Machine Learning'],
            },
            {
                'title': 'Autonomous Navigation & SLAM Research Project',
                'organization': 'Robotics Autonomy Center',
                'description': 'Investigate visual inertial odometry and real-time point-cloud semantic segmentation for autonomous drone mapping.',
                'type': 'Research', 'domain': 'Robotics & Automation', 'loc': 'Chennai', 'mode': 'Offline',
                'dur': '5 Months', 'cgpa': 7.5, 'days': 38, 'url': 'https://example.com/research/slam-autonomy',
                'branches': ['CSE', 'ECE', 'ME'], 'years': [3, 4, 5],
                'req_skills': ['C++', 'Python', 'Computer Vision', 'Data Structures & Algorithms'],
                'interests': ['Robotics & Automation', 'Autonomous Systems', 'Computer Vision'],
            },
            {
                'title': 'Post-Quantum Cryptography & Secure Protocols Study',
                'organization': 'Center for Quantum & Cyber Resilience',
                'description': 'Analyze lattice-based cryptographic algorithms, side-channel attack vulnerabilities, and hardware implementation constraints.',
                'type': 'Research', 'domain': 'Cybersecurity', 'loc': 'Remote', 'mode': 'Online',
                'dur': '6 Months', 'cgpa': 8.0, 'days': 50, 'url': 'https://example.com/research/post-quantum',
                'branches': ['CSE', 'IT', 'ECE'], 'years': [3, 4, 5],
                'req_skills': ['Cybersecurity', 'C++', 'Data Structures & Algorithms', 'Linux Administration'],
                'interests': ['Cybersecurity', 'Quantum Computing', 'Network Security'],
            },
            {
                'title': 'Computational Genomics & Protein Structure Research',
                'organization': 'BioTech Discovery Institute',
                'description': 'Apply deep geometric learning models to predict macromolecular ligand binding and enzyme pocket conformational shifts.',
                'type': 'Research', 'domain': 'Bioinformatics', 'loc': 'Remote', 'mode': 'Online',
                'dur': '4 Months', 'cgpa': 7.8, 'days': 42, 'url': 'https://example.com/research/genomics-ai',
                'branches': ['CSE', 'IT', 'AI&DS'], 'years': [3, 4, 5],
                'req_skills': ['Python', 'PyTorch', 'Data Analysis', 'Pandas'],
                'interests': ['Bioinformatics', 'Machine Learning', 'Data Science'],
            },

            # Competitions
            {
                'title': 'National Algorithmic Coding Championship 2026',
                'organization': 'CodeMaster Arena',
                'description': 'Tier-1 competitive programming battle with individual rounds testing dynamic programming, graph theory, flow networks, and string matching.',
                'type': 'Competition', 'domain': 'Competitive Programming', 'loc': 'Online', 'mode': 'Online',
                'dur': '1 Day', 'cgpa': 0.0, 'days': 8, 'url': 'https://example.com/competitions/algo-championship',
                'branches': [], 'years': [],
                'req_skills': ['Data Structures & Algorithms', 'C++', 'Python', 'Java'],
                'interests': ['Competitive Programming'],
            },
            {
                'title': 'Inter-Collegiate UI/UX Design Sprint Competition',
                'organization': 'Creative Minds Collective',
                'description': 'Design challenge to conceptualize, prototype, and user-test an accessible fintech onboarding workflow within 36 hours.',
                'type': 'Competition', 'domain': 'UI/UX Design', 'loc': 'Virtual', 'mode': 'Online',
                'dur': '2 Days', 'cgpa': 0.0, 'days': 11, 'url': 'https://example.com/competitions/design-sprint',
                'branches': [], 'years': [],
                'req_skills': ['Figma', 'UI/UX Design', 'HTML5/CSS3'],
                'interests': ['UI/UX Design'],
            },
            {
                'title': 'Kaggle Grand Data Olympiad 2026',
                'organization': 'Predictive Insights Guild',
                'description': 'Multi-phase predictive modeling competition evaluating feature engineering and ensemble algorithms on tabular and text datasets.',
                'type': 'Competition', 'domain': 'Data Science', 'loc': 'Online', 'mode': 'Online',
                'dur': '3 Weeks', 'cgpa': 0.0, 'days': 24, 'url': 'https://example.com/competitions/data-olympiad',
                'branches': [], 'years': [],
                'req_skills': ['Python', 'Machine Learning', 'Pandas', 'NumPy', 'Scikit-Learn'],
                'interests': ['Data Science', 'Machine Learning'],
            },

            # Fellowships
            {
                'title': 'Open Source Software Engineering Fellowship',
                'organization': 'Global Open Source Collective',
                'description': 'Paid 12-week fellowship contributing production-grade features, unit tests, and performance patches to top GitHub developer tools.',
                'type': 'Fellowship', 'domain': 'Open Source Software', 'loc': 'Remote', 'mode': 'Online',
                'dur': '3 Months', 'cgpa': 7.0, 'days': 27, 'url': 'https://example.com/fellowships/open-source',
                'branches': ['CSE', 'IT'], 'years': [2, 3, 4],
                'req_skills': ['Git', 'Python', 'TypeScript', 'Unit Testing', 'CI/CD Pipelines'],
                'interests': ['Open Source Software', 'Web Development'],
            },
            {
                'title': 'Kavli Young Innovators Climate Tech Fellowship',
                'organization': 'EcoVentures Foundation',
                'description': 'Interdisciplinary fellowship funding student-driven software platforms tackling carbon footprint accounting and grid load optimization.',
                'type': 'Fellowship', 'domain': 'Green Computing', 'loc': 'Hybrid', 'mode': 'Hybrid',
                'dur': '6 Months', 'cgpa': 7.5, 'days': 34, 'url': 'https://example.com/fellowships/climate-tech',
                'branches': ['CSE', 'IT', 'EEE', 'ME'], 'years': [3, 4],
                'req_skills': ['Python', 'Data Analysis', 'SQL'],
                'interests': ['Green Computing', 'Data Science'],
            },
            {
                'title': 'Pioneer Venture & Entrepreneurship Fellowship',
                'organization': 'Campus Incubator Alliance',
                'description': 'Seed funding, legal setup assistance, and mentorship from serial founders for technical students launching early-stage startups.',
                'type': 'Fellowship', 'domain': 'Entrepreneurship', 'loc': 'Bengaluru', 'mode': 'Offline',
                'dur': '6 Months', 'cgpa': 6.5, 'days': 31, 'url': 'https://example.com/fellowships/pioneer-venture',
                'branches': [], 'years': [3, 4],
                'req_skills': ['System Design', 'Agile / Scrum'],
                'interests': ['FinTech', 'EdTech', 'HealthTech'],
            },

            # Workshops
            {
                'title': 'Hands-on Microservices Architecture with Docker & K8s',
                'organization': 'DevOps Masters Academy',
                'description': 'Intensive 3-weekend bootcamp building containerized microservices, service meshes, zero-downtime rolling updates, and Prometheus metrics.',
                'type': 'Workshop', 'domain': 'Cloud & DevOps', 'loc': 'Remote', 'mode': 'Online',
                'dur': '3 Weeks', 'cgpa': 0.0, 'days': 9, 'url': 'https://example.com/workshops/microservices-k8s',
                'branches': ['CSE', 'IT', 'ECE'], 'years': [2, 3, 4],
                'req_skills': ['Docker', 'Kubernetes', 'Linux Administration', 'Git'],
                'interests': ['Cloud Computing', 'DevOps & SRE', 'API & Microservices Architecture'],
            },
            {
                'title': 'Building Production GenAI Applications with RAG & LangChain',
                'organization': 'AI Engineers Guild',
                'description': 'Deep dive into vector databases, retrieval-augmented generation (RAG), embedding fine-tuning, and semantic caching.',
                'type': 'Workshop', 'domain': 'Artificial Intelligence', 'loc': 'Online', 'mode': 'Online',
                'dur': '2 Weeks', 'cgpa': 0.0, 'days': 13, 'url': 'https://example.com/workshops/genai-rag',
                'branches': ['CSE', 'IT', 'AI&DS'], 'years': [2, 3, 4],
                'req_skills': ['Python', 'FastAPI', 'SQL', 'Git'],
                'interests': ['Artificial Intelligence', 'Natural Language Processing'],
            },
            {
                'title': 'Advanced System Design & Scalability Masterclass',
                'organization': 'HighScale Systems Group',
                'description': 'Learn partitioning, consistent hashing, caching strategies, distributed consensus, and event-driven architectures from principal architects.',
                'type': 'Workshop', 'domain': 'Distributed Systems', 'loc': 'Online', 'mode': 'Online',
                'dur': '1 Month', 'cgpa': 0.0, 'days': 19, 'url': 'https://example.com/workshops/system-design',
                'branches': ['CSE', 'IT'], 'years': [3, 4],
                'req_skills': ['System Design', 'SQL', 'Redis', 'PostgreSQL'],
                'interests': ['Distributed Systems', 'Database Systems', 'API & Microservices Architecture'],
            },
            {
                'title': 'Modern Frontend with React 19, Next.js & Tailwind',
                'organization': 'CodeCraft Studios',
                'description': 'Master React server components, server actions, streaming SSR, and modern component composition.',
                'type': 'Workshop', 'domain': 'Web Development', 'loc': 'Online', 'mode': 'Online',
                'dur': '2 Weeks', 'cgpa': 0.0, 'days': 16, 'url': 'https://example.com/workshops/nextjs-mastery',
                'branches': [], 'years': [],
                'req_skills': ['JavaScript', 'TypeScript', 'React', 'HTML5/CSS3'],
                'interests': ['Web Development', 'UI/UX Design'],
            },

            # Training Programs
            {
                'title': 'AWS Certified Cloud Practitioner Bootcamp',
                'organization': 'CloudPath Institute',
                'description': 'Structured 8-week corporate training curriculum covering AWS compute, storage, security, VPC networking, and cost optimization.',
                'type': 'Training', 'domain': 'Cloud Computing', 'loc': 'Online', 'mode': 'Online',
                'dur': '2 Months', 'cgpa': 6.0, 'days': 23, 'url': 'https://example.com/training/aws-practitioner',
                'branches': [], 'years': [1, 2, 3, 4],
                'req_skills': ['Linux Administration', 'Git'],
                'interests': ['Cloud Computing'],
            },
            {
                'title': 'Full-Stack Django & Modern Web Development Accelerator',
                'organization': 'PyAcademy Global',
                'description': 'End-to-end hands-on training creating secure, database-backed enterprise applications with Django, PostgreSQL, Celery, and Bootstrap.',
                'type': 'Training', 'domain': 'Web Development', 'loc': 'Online', 'mode': 'Online',
                'dur': '3 Months', 'cgpa': 6.0, 'days': 33, 'url': 'https://example.com/training/django-accelerator',
                'branches': ['CSE', 'IT', 'ECE'], 'years': [2, 3, 4],
                'req_skills': ['Python', 'Django', 'SQL', 'HTML5/CSS3', 'Git'],
                'interests': ['Web Development', 'API & Microservices Architecture'],
            },
            {
                'title': 'Defensive Cybersecurity & SOC Analyst Program',
                'organization': 'SecureNode Academy',
                'description': 'Practical training on security information and event management (SIEM), threat hunting, packet inspection, and incident response playbooks.',
                'type': 'Training', 'domain': 'Cybersecurity', 'loc': 'Hyderabad', 'mode': 'Hybrid',
                'dur': '3 Months', 'cgpa': 6.5, 'days': 26, 'url': 'https://example.com/training/soc-analyst',
                'branches': ['CSE', 'IT', 'ECE'], 'years': [3, 4],
                'req_skills': ['Cybersecurity', 'Linux Administration', 'Python'],
                'interests': ['Cybersecurity', 'Network Security'],
            },

            # Certifications
            {
                'title': 'Certified Kubernetes Administrator (CKA) Voucher Program',
                'organization': 'Cloud Native Compute Initiative',
                'description': 'Subsidized certification training and examination voucher program for promising systems and cloud computing students.',
                'type': 'Certification', 'domain': 'Cloud & DevOps', 'loc': 'Online', 'mode': 'Online',
                'dur': 'Self-Paced', 'cgpa': 7.0, 'days': 44, 'url': 'https://example.com/certs/cka-voucher',
                'branches': ['CSE', 'IT'], 'years': [3, 4],
                'req_skills': ['Kubernetes', 'Docker', 'Linux Administration'],
                'interests': ['Cloud Computing', 'DevOps & SRE'],
            },
            {
                'title': 'TensorFlow Professional Developer Certification Grant',
                'organization': 'Deep Learning Society',
                'description': 'Comprehensive exam preparation materials and subsidized voucher for the Google TensorFlow developer exam.',
                'type': 'Certification', 'domain': 'AI & Data Science', 'loc': 'Online', 'mode': 'Online',
                'dur': '6 Weeks', 'cgpa': 7.2, 'days': 37, 'url': 'https://example.com/certs/tensorflow-grant',
                'branches': ['CSE', 'IT', 'AI&DS'], 'years': [2, 3, 4],
                'req_skills': ['Python', 'TensorFlow', 'NumPy', 'Machine Learning'],
                'interests': ['Artificial Intelligence', 'Machine Learning'],
            },
            {
                'title': 'Meta Certified Front-End Developer Program',
                'organization': 'Frontend Leaders Consortium',
                'description': 'Official industry certification credential in responsive web design, client-side routing, state management, and accessibility.',
                'type': 'Certification', 'domain': 'Web Development', 'loc': 'Online', 'mode': 'Online',
                'dur': '2 Months', 'cgpa': 0.0, 'days': 41, 'url': 'https://example.com/certs/meta-frontend',
                'branches': [], 'years': [],
                'req_skills': ['JavaScript', 'React', 'HTML5/CSS3', 'Git', 'UI/UX Design'],
                'interests': ['Web Development', 'UI/UX Design'],
            },

            # Additional Diverse Opportunities (reaching 40+)
            {
                'title': 'Computer Vision & Augmented Reality Fellowship',
                'organization': 'Immerse Vision Labs',
                'description': 'Develop 3D spatial mapping and gesture tracking algorithms using OpenCV, PyTorch, and WebXR.',
                'type': 'Fellowship', 'domain': 'AR/VR & Metaverse', 'loc': 'Remote', 'mode': 'Online',
                'dur': '4 Months', 'cgpa': 7.5, 'days': 20, 'url': 'https://example.com/fellowships/ar-vision',
                'branches': ['CSE', 'IT', 'AI&DS'], 'years': [3, 4],
                'req_skills': ['Python', 'Computer Vision', 'C++', 'PyTorch'],
                'interests': ['Computer Vision', 'AR/VR & Metaverse', 'Artificial Intelligence'],
            },
            {
                'title': 'Robotics Hardware & Automation Co-Op',
                'organization': 'Titan Industrial Automation',
                'description': 'Design mechanical linkages, motor PID controllers, and PLC safety interlocks for automated warehouse transport bots.',
                'type': 'Internship', 'domain': 'Robotics & Automation', 'loc': 'Chennai', 'mode': 'Offline',
                'dur': '6 Months', 'cgpa': 7.0, 'days': 22, 'url': 'https://example.com/apply/titan-robotics',
                'branches': ['ME', 'ECE', 'EEE'], 'years': [3, 4],
                'req_skills': ['C++', 'Data Structures & Algorithms'],
                'interests': ['Robotics & Automation', 'Autonomous Systems'],
            },
            {
                'title': 'National Smart Mobility Hackathon',
                'organization': 'Ministry of Urban Transport',
                'description': 'Develop route optimization and multi-modal fleet dispatch algorithms for metro and electric bus networks.',
                'type': 'Hackathon', 'domain': 'Autonomous Systems', 'loc': 'Delhi', 'mode': 'Offline',
                'dur': '2 Days', 'cgpa': 0.0, 'days': 17, 'url': 'https://example.com/hackathons/smart-mobility',
                'branches': ['CSE', 'IT', 'AI&DS', 'CE'], 'years': [2, 3, 4],
                'req_skills': ['Python', 'Data Structures & Algorithms', 'Data Analysis'],
                'interests': ['Autonomous Systems', 'Green Computing'],
            },
            {
                'title': 'AI Safety & Alignment Summer Research Residency',
                'organization': 'Global AI Alignment Initiative',
                'description': 'Work with leading scholars studying reward hacking, red-teaming foundation models, and scalable automated oversight mechanisms.',
                'type': 'Research', 'domain': 'Artificial Intelligence', 'loc': 'Remote', 'mode': 'Online',
                'dur': '3 Months', 'cgpa': 8.5, 'days': 48, 'url': 'https://example.com/research/ai-safety',
                'branches': ['CSE', 'IT', 'AI&DS'], 'years': [3, 4, 5],
                'req_skills': ['Python', 'PyTorch', 'Natural Language Processing', 'Machine Learning'],
                'interests': ['Artificial Intelligence', 'Machine Learning', 'Natural Language Processing'],
            },
            {
                'title': 'Edge AI & Embedded Machine Learning Workshop',
                'organization': 'SiliconEdge Labs',
                'description': 'Deploy quantized neural networks onto microcontrollers (TinyML) and optimize inference latency on edge devices.',
                'type': 'Workshop', 'domain': 'Edge Computing', 'loc': 'Bangalore', 'mode': 'Hybrid',
                'dur': '3 Weeks', 'cgpa': 6.5, 'days': 15, 'url': 'https://example.com/workshops/tiny-ml',
                'branches': ['ECE', 'CSE', 'EEE'], 'years': [3, 4],
                'req_skills': ['Python', 'C++', 'TensorFlow', 'Machine Learning'],
                'interests': ['IoT (Internet of Things)', 'Artificial Intelligence'],
            },
            {
                'title': 'Google Summer of Code Mentorship Preparation Program',
                'organization': 'Campus Open Source Guild',
                'description': 'Mentorship boot-camp guiding students through open source contribution workflows, IRC/mailing list communication, and GSoC proposal drafting.',
                'type': 'Training', 'domain': 'Open Source Software', 'loc': 'Online', 'mode': 'Online',
                'dur': '6 Weeks', 'cgpa': 0.0, 'days': 12, 'url': 'https://example.com/training/gsoc-prep',
                'branches': [], 'years': [1, 2, 3, 4],
                'req_skills': ['Git', 'Python', 'Unit Testing'],
                'interests': ['Open Source Software'],
            },
            {
                'title': 'National Cybersecurity Capture The Flag (CTF) Challenge',
                'organization': 'CyberGuard League',
                'description': 'Team-based 24-hour CTF challenge covering binary exploitation, cryptography, reverse engineering, web vulnerabilities, and forensics.',
                'type': 'Competition', 'domain': 'Cybersecurity', 'loc': 'Online', 'mode': 'Online',
                'dur': '1 Day', 'cgpa': 0.0, 'days': 7, 'url': 'https://example.com/competitions/cyber-ctf',
                'branches': [], 'years': [],
                'req_skills': ['Cybersecurity', 'Ethical Hacking', 'Linux Administration', 'Python'],
                'interests': ['Cybersecurity', 'Network Security'],
            },
        ]

        created_opp_count = 0
        today = timezone.now().date()

        for d in opp_data:
            deadline_date = today + timedelta(days=d['days'])
            opp, created = Opportunity.objects.get_or_create(
                title=d['title'],
                organization=d['organization'],
                defaults={
                    'description': d['description'],
                    'opportunity_type': d['type'],
                    'domain': d['domain'],
                    'location': d['loc'],
                    'mode': d['mode'],
                    'duration': d['dur'],
                    'minimum_cgpa': d['cgpa'],
                    'deadline': deadline_date,
                    'application_url': d['url'],
                    'is_active': True,
                }
            )
            # Add relational connections
            if d.get('branches'):
                branch_objs = [branches[c] for c in d['branches'] if c in branches]
                opp.eligible_branches.set(branch_objs)
            if d.get('years'):
                year_objs = [years[y] for y in d['years'] if y in years]
                opp.eligible_years.set(year_objs)
            if d.get('req_skills'):
                skill_objs = [skills[s] for s in d['req_skills'] if s in skills]
                opp.required_skills.set(skill_objs)
            if d.get('interests'):
                interest_objs = [interests[i] for i in d['interests'] if i in interests]
                opp.interests.set(interest_objs)

            opp.save()
            created_opp_count += 1

        self.stdout.write(self.style.SUCCESS(f"Seeded {created_opp_count} Opportunities across 9 categories!"))

        # 7. 30+ Realistic Students
        # Include specific primary demo student: Sai Krishna (IT, 3rd Year, CGPA 8.0, Python, Django, SQL, AI/ML)
        students_roster = [
            {
                'username': 'saikrishna',
                'first_name': 'Sai',
                'last_name': 'Krishna',
                'email': 'saikrishna@student.edu',
                'college': 'Indian Institute of Technology (IIT)',
                'branch': 'IT',
                'year': 3,
                'cgpa': 8.0,
                'bio': 'Passionate 3rd-year IT undergraduate specializing in full-stack web platforms and applied machine learning.',
                'preferred_mode': 'Online',
                'preferred_type': 'Internship',
                'preferred_duration': '3-6 Months',
                'preferred_loc': 'Remote',
                'availability': 'Immediate',
                'skills': [
                    ('Python', 'Advanced'),
                    ('Django', 'Intermediate'),
                    ('SQL', 'Intermediate'),
                    ('Machine Learning', 'Intermediate'),
                    ('Data Analysis', 'Beginner'),
                ],
                'interests': ['Artificial Intelligence', 'Machine Learning', 'Web Development'],
            },
            {
                'username': 'ananya_sharma',
                'first_name': 'Ananya',
                'last_name': 'Sharma',
                'email': 'ananya.sharma@university.edu',
                'college': 'National Institute of Technology',
                'branch': 'CSE',
                'year': 4,
                'cgpa': 8.9,
                'bio': 'Final year CS major with deep interest in distributed systems, Kubernetes, and cloud infrastructure.',
                'preferred_mode': 'Online',
                'preferred_type': 'Internship',
                'preferred_duration': '3-6 Months',
                'preferred_loc': 'Remote',
                'availability': 'Immediate',
                'skills': [('Python', 'Advanced'), ('Docker', 'Advanced'), ('Kubernetes', 'Intermediate'), ('AWS', 'Intermediate'), ('Git', 'Expert')],
                'interests': ['Cloud Computing', 'DevOps & SRE', 'Distributed Systems'],
            },
            {
                'username': 'rohit_verma',
                'first_name': 'Rohit',
                'last_name': 'Verma',
                'email': 'rohit.verma@college.edu',
                'college': 'BITS Pilani',
                'branch': 'AI&DS',
                'year': 3,
                'cgpa': 8.6,
                'bio': 'Focused on deep neural networks, computer vision, and foundation models.',
                'preferred_mode': 'Any',
                'preferred_type': 'Research',
                'preferred_duration': '3-6 Months',
                'preferred_loc': 'Remote',
                'availability': 'Immediate',
                'skills': [('Python', 'Expert'), ('PyTorch', 'Advanced'), ('Computer Vision', 'Intermediate'), ('Git', 'Intermediate'), ('SQL', 'Beginner')],
                'interests': ['Artificial Intelligence', 'Computer Vision', 'Machine Learning'],
            },
            {
                'username': 'priya_nair',
                'first_name': 'Priya',
                'last_name': 'Nair',
                'email': 'priya.nair@inst.edu',
                'college': 'Vellore Institute of Technology',
                'branch': 'IT',
                'year': 2,
                'cgpa': 8.2,
                'bio': 'Frontend engineer crafting intuitive web applications and accessible UI components.',
                'preferred_mode': 'Online',
                'preferred_type': 'Hackathon',
                'preferred_duration': '1-2 Months',
                'preferred_loc': 'Remote',
                'availability': 'Flexible',
                'skills': [('JavaScript', 'Advanced'), ('React', 'Advanced'), ('HTML5/CSS3', 'Expert'), ('Figma', 'Intermediate'), ('Git', 'Intermediate')],
                'interests': ['Web Development', 'UI/UX Design'],
            },
            {
                'username': 'rahul_singh',
                'first_name': 'Rahul',
                'last_name': 'Singh',
                'email': 'rahul.s@tech.edu',
                'college': 'Delhi Technological University',
                'branch': 'ECE',
                'year': 3,
                'cgpa': 7.4,
                'bio': 'Hardware and embedded enthusiast exploring autonomous robotics and IoT sensors.',
                'preferred_mode': 'Offline',
                'preferred_type': 'Internship',
                'preferred_duration': '3-6 Months',
                'preferred_loc': 'Delhi',
                'availability': 'Immediate',
                'skills': [('C++', 'Advanced'), ('Linux Administration', 'Intermediate'), ('Data Structures & Algorithms', 'Intermediate')],
                'interests': ['IoT (Internet of Things)', 'Robotics & Automation'],
            },
            {
                'username': 'sneha_patel',
                'first_name': 'Sneha',
                'last_name': 'Patel',
                'email': 'sneha.p@engineering.edu',
                'college': 'College of Engineering Pune',
                'branch': 'CSE',
                'year': 3,
                'cgpa': 9.1,
                'bio': 'Competitive programmer and systems developer with strong algorithmic problem solving skills.',
                'preferred_mode': 'Any',
                'preferred_type': 'Competition',
                'preferred_duration': 'Any',
                'preferred_loc': 'Remote',
                'availability': 'Immediate',
                'skills': [('C++', 'Expert'), ('Java', 'Advanced'), ('Data Structures & Algorithms', 'Expert'), ('Python', 'Intermediate'), ('SQL', 'Intermediate')],
                'interests': ['Competitive Programming', 'Distributed Systems'],
            },
            {
                'username': 'arjun_reddy',
                'first_name': 'Arjun',
                'last_name': 'Reddy',
                'email': 'arjun.r@univ.edu',
                'college': 'IIIT Hyderabad',
                'branch': 'CSE',
                'year': 4,
                'cgpa': 8.4,
                'bio': 'Cybersecurity researcher passionate about web application penetration testing and secure code audits.',
                'preferred_mode': 'Online',
                'preferred_type': 'Internship',
                'preferred_duration': '3-6 Months',
                'preferred_loc': 'Remote',
                'availability': 'Immediate',
                'skills': [('Cybersecurity', 'Advanced'), ('Ethical Hacking', 'Advanced'), ('Linux Administration', 'Advanced'), ('Python', 'Intermediate'), ('Git', 'Intermediate')],
                'interests': ['Cybersecurity', 'Network Security'],
            },
            {
                'username': 'kavya_iyer',
                'first_name': 'Kavya',
                'last_name': 'Iyer',
                'email': 'kavya.i@college.edu',
                'college': 'PSG College of Technology',
                'branch': 'CSE',
                'year': 2,
                'cgpa': 7.8,
                'bio': 'Full-stack web learner exploring Node.js, databases, and microservices.',
                'preferred_mode': 'Online',
                'preferred_type': 'Training',
                'preferred_duration': '1-2 Months',
                'preferred_loc': 'Remote',
                'availability': 'Immediate',
                'skills': [('JavaScript', 'Intermediate'), ('Node.js', 'Intermediate'), ('Express.js', 'Intermediate'), ('MongoDB', 'Beginner'), ('Git', 'Intermediate')],
                'interests': ['Web Development', 'API & Microservices Architecture'],
            },
            {
                'username': 'vikram_malhotra',
                'first_name': 'Vikram',
                'last_name': 'Malhotra',
                'email': 'vikram.m@tech.edu',
                'college': 'Manipal Institute of Technology',
                'branch': 'IT',
                'year': 3,
                'cgpa': 7.9,
                'bio': 'Building cross-platform apps and learning cloud backend integrations.',
                'preferred_mode': 'Online',
                'preferred_type': 'Internship',
                'preferred_duration': '3-6 Months',
                'preferred_loc': 'Remote',
                'availability': 'Immediate',
                'skills': [('Flutter', 'Advanced'), ('Dart', 'Advanced' if 'Dart' in skills else 'Intermediate'), ('RESTful APIs', 'Intermediate'), ('Git', 'Intermediate')],
                'interests': ['Mobile App Development', 'UI/UX Design'],
            },
            {
                'username': 'divya_joshi',
                'first_name': 'Divya',
                'last_name': 'Joshi',
                'email': 'divya.j@university.edu',
                'college': 'Thapar Institute',
                'branch': 'AI&DS',
                'year': 2,
                'cgpa': 8.5,
                'bio': 'Exploring exploratory data analysis, statistics, and machine learning models.',
                'preferred_mode': 'Online',
                'preferred_type': 'Hackathon',
                'preferred_duration': '1-2 Months',
                'preferred_loc': 'Remote',
                'availability': 'Flexible',
                'skills': [('Python', 'Advanced'), ('Pandas', 'Advanced'), ('NumPy', 'Intermediate'), ('SQL', 'Intermediate'), ('Data Analysis', 'Advanced')],
                'interests': ['Data Science', 'Machine Learning'],
            },
            # 20 More Students to make 30+
            ('karan_kapoor', 'Karan', 'Kapoor', 'CSE', 3, 7.6, 'Bangalore Tech Univ', 'Cloud & Docker learner', ['Python', 'Docker', 'Linux Administration'], ['Cloud Computing']),
            ('tanvi_sen', 'Tanvi', 'Sen', 'IT', 4, 8.8, 'Jadavpur University', 'Natural language processing researcher', ['Python', 'Natural Language Processing', 'PyTorch', 'Git'], ['Artificial Intelligence', 'Natural Language Processing']),
            ('manish_tiwari', 'Manish', 'Tiwari', 'ECE', 2, 7.1, 'NIT Trichy', 'Embedded C & IoT developer', ['C++', 'Linux Administration'], ['IoT (Internet of Things)']),
            ('ishita_bose', 'Ishita', 'Bose', 'CSE', 3, 8.3, 'Heritage Institute', 'Java and Spring microservices developer', ['Java', 'Spring Boot', 'SQL', 'PostgreSQL'], ['Web Development', 'FinTech']),
            ('deepak_kumar', 'Deepak', 'Kumar', 'AI&DS', 3, 7.7, 'SRM University', 'Machine learning and deep learning enthusiast', ['Python', 'Scikit-Learn', 'Pandas', 'Machine Learning'], ['Artificial Intelligence', 'Machine Learning']),
            ('aisha_khan', 'Aisha', 'Khan', 'IT', 2, 8.0, 'Amity University', 'React and modern web designer', ['React', 'JavaScript', 'HTML5/CSS3', 'Figma'], ['Web Development', 'UI/UX Design']),
            ('siddharth_das', 'Siddharth', 'Das', 'CSE', 4, 9.0, 'IIT Kharagpur', 'Open source contributor and Rust programmer', ['Rust', 'Python', 'Git', 'Linux Administration'], ['Open Source Software', 'Distributed Systems']),
            ('neha_rao', 'Neha', 'Rao', 'CSBS', 3, 7.8, 'RV College of Engineering', 'Business systems analyst and SQL modeler', ['SQL', 'Python', 'Data Analysis', 'Agile / Scrum'], ['FinTech', 'Data Science']),
            ('mohit_jain', 'Mohit', 'Jain', 'ME', 3, 7.3, 'MIT Manipal', 'Robotics and CAD systems enthusiast', ['C++', 'Data Structures & Algorithms'], ['Robotics & Automation']),
            ('riya_chatterjee', 'Riya', 'Chatterjee', 'CSE', 1, 8.5, 'St. Xaviers Tech', 'Aspiring software developer learning fundamentals', ['Python', 'C++', 'Data Structures & Algorithms'], ['Competitive Programming']),
            ('harsh_vardhan', 'Harsh', 'Vardhan', 'IT', 3, 7.5, 'Lovely Professional Univ', 'Full stack developer exploring Django', ['Python', 'Django', 'SQL', 'Git'], ['Web Development']),
            ('shreya_menon', 'Shreya', 'Menon', 'AI&DS', 4, 8.7, 'Amrita Vishwa Vidyapeetham', 'Computer vision and medical imaging researcher', ['Python', 'PyTorch', 'Computer Vision', 'OpenCV' if 'OpenCV' in skills else 'Git'], ['Computer Vision', 'HealthTech']),
            ('aditya_kulkarni', 'Aditya', 'Kulkarni', 'CSE', 3, 8.1, 'COEP Technological Univ', 'Backend engineer learning Go and microservices', ['Go', 'Docker', 'PostgreSQL', 'Git'], ['Distributed Systems', 'Cloud Computing']),
            ('meera_krishnan', 'Meera', 'Krishnan', 'IT', 2, 7.9, 'SSN College of Engineering', 'Flutter mobile application creator', ['Flutter', 'RESTful APIs', 'Git'], ['Mobile App Development']),
            ('varun_shukla', 'Varun', 'Shukla', 'ECE', 4, 8.0, 'MNIT Jaipur', 'FPGA and low power hardware designer', ['C++', 'Linux Administration'], ['IoT (Internet of Things)']),
            ('pooja_deshmukh', 'Pooja', 'Deshmukh', 'CSE', 3, 8.4, 'Walchand College', 'DevOps and cloud engineer', ['Docker', 'AWS', 'Linux Administration', 'Git'], ['Cloud Computing', 'DevOps & SRE']),
            ('yash_bhatt', 'Yash', 'Bhatt', 'IT', 3, 7.6, 'Nirma University', 'Web security and ethical hacker', ['Cybersecurity', 'Ethical Hacking', 'Linux Administration'], ['Cybersecurity']),
            ('anjali_gupta', 'Anjali', 'Gupta', 'AI&DS', 3, 8.6, 'BMS College', 'Data scientist building predictive analytics models', ['Python', 'Pandas', 'Scikit-Learn', 'SQL'], ['Data Science', 'Machine Learning']),
            ('naveen_kumar', 'Naveen', 'Kumar', 'CSE', 4, 8.2, 'Osmania University', 'Java backend developer with microservices focus', ['Java', 'Spring Boot', 'SQL', 'Docker'], ['Web Development']),
            ('tanya_saxena', 'Tanya', 'Saxena', 'IT', 3, 8.3, 'Jaypee Institute', 'UI/UX designer and frontend developer', ['Figma', 'UI/UX Design', 'React', 'HTML5/CSS3'], ['UI/UX Design', 'Web Development']),
        ]

        created_students = []
        for item in students_roster:
            if isinstance(item, dict):
                username = item['username']
                first_name = item['first_name']
                last_name = item['last_name']
                email = item['email']
                college = item['college']
                b_code = item['branch']
                yr_num = item['year']
                cgpa = item['cgpa']
                bio = item['bio']
                mode = item['preferred_mode']
                opp_type = item['preferred_type']
                dur = item['preferred_duration']
                loc = item['preferred_loc']
                avail = item['availability']
                skill_tuples = item['skills']
                interest_names = item['interests']
            else:
                (username, first_name, last_name, b_code, yr_num, cgpa, college, bio, skill_list, interest_names) = item
                email = f"{username}@example.edu"
                mode = 'Online'
                opp_type = 'Any'
                dur = 'Any'
                loc = 'Remote'
                avail = 'Immediate'
                skill_tuples = [(s, 'Intermediate') for s in skill_list]

            user, u_created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                }
            )
            if u_created or not user.has_usable_password():
                user.set_password('password123')
                user.save()

            profile, _ = StudentProfile.objects.get_or_create(
                user=user,
                defaults={
                    'college': college,
                    'branch': branches.get(b_code),
                    'year': years.get(yr_num),
                    'cgpa': cgpa,
                    'bio': bio,
                    'preferred_mode': mode,
                    'preferred_type': opp_type,
                    'preferred_duration': dur,
                    'preferred_location': loc,
                    'availability': avail,
                }
            )

            # Assign skills
            for s_name, s_level in skill_tuples:
                if s_name in skills:
                    StudentSkill.objects.update_or_create(
                        student=profile,
                        skill=skills[s_name],
                        defaults={'skill_level': s_level}
                    )

            # Assign interests
            int_objs = [interests[i] for i in interest_names if i in interests]
            profile.interests.set(int_objs)
            profile.save()

            created_students.append(profile)

        self.stdout.write(self.style.SUCCESS(f"Seeded {len(created_students)} Student profiles!"))

        # 8. Execute Deterministic Matching Engine for all students
        self.stdout.write("Running automatic matching engine for all seeded students...")
        for student in created_students:
            run_matching_engine_for_student(student, save_to_db=True)

        # 9. Create some realistic Saved Opportunities and Applications for Sai Krishna & other students
        sai_profile = StudentProfile.objects.filter(user__username='saikrishna').first()
        if sai_profile:
            # Save 2 opportunities
            sample_opps = list(Opportunity.objects.filter(is_active=True)[:4])
            if sample_opps:
                SavedOpportunity.objects.get_or_create(student=sai_profile, opportunity=sample_opps[0])
                SavedOpportunity.objects.get_or_create(student=sai_profile, opportunity=sample_opps[1])
                # Track 1 application
                Application.objects.get_or_create(
                    student=sai_profile,
                    opportunity=sample_opps[0],
                    defaults={'status': 'Under Review', 'notes': 'Applied with updated GitHub portfolio.'}
                )
                Application.objects.get_or_create(
                    student=sai_profile,
                    opportunity=sample_opps[2],
                    defaults={'status': 'Applied', 'notes': 'Application submitted via university portal.'}
                )

                # Add sample notification
                Notification.objects.get_or_create(
                    student=sai_profile,
                    title="[MATCH] High Compatibility Match Found!",
                    defaults={
                        'message': f"The system found a 94% match with '{sample_opps[0].title}' based on your Python and AI profile.",
                        'notification_type': 'match',
                    }
                )
                Notification.objects.get_or_create(
                    student=sai_profile,
                    title="[RECOMMENDATION] Skill Recommendation",
                    defaults={
                        'message': "Adding 'Git' and 'Docker' would increase your compatibility with 15+ relevant opportunities.",
                        'notification_type': 'skill',
                    }
                )

        self.stdout.write(self.style.SUCCESS("[SUCCESS] Seed data generation complete!"))
        self.stdout.write(self.style.SUCCESS("Admin account: admin / admin123"))
        self.stdout.write(self.style.SUCCESS("Demo student: saikrishna / password123"))
