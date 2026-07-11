"""
Usage: python manage.py seed_jobs
Seeds realistic job listings into the database.
"""
from django.core.management.base import BaseCommand
from api.models import JobListing


JOBS = [
    # Python / Data
    ('Data Scientist',          'Google',       'Python, Machine Learning, SQL, Statistics, Pandas',         18.0,  165000),
    ('Data Scientist',          'Amazon',       'Python, Machine Learning, Deep Learning, SQL',              22.0,  202000),
    ('Data Scientist',          'Microsoft',    'Python, SQL, Statistics, Machine Learning, Pandas',         20.0,  184000),
    ('Data Scientist',          'TCS',          'Python, SQL, Data Analysis, Machine Learning',              10.0,   92000),
    ('Data Scientist',          'Infosys',      'Python, SQL, Statistics, Pandas',                            9.0,   82800),
    ('Data Scientist',          'Wipro',        'Python, Machine Learning, SQL, Data Analysis',               8.5,   78200),

    # ML Engineer
    ('ML Engineer',             'Google',       'Python, Machine Learning, Deep Learning, TensorFlow',       25.0,  230000),
    ('ML Engineer',             'Amazon',       'Python, Machine Learning, PyTorch, Deep Learning',          28.0,  257600),
    ('ML Engineer',             'Netflix',      'Python, Machine Learning, TensorFlow, Scikit-learn',        32.0,  294400),
    ('ML Engineer',             'Startup',      'Python, Machine Learning, Deep Learning',                   14.0,  128800),
    ('ML Engineer',             'Flipkart',     'Python, Machine Learning, SQL, TensorFlow',                 18.0,  165600),

    # Data Analyst
    ('Data Analyst',            'Google',       'Python, SQL, Data Analysis, Pandas, Visualization',        12.0,  110400),
    ('Data Analyst',            'Amazon',       'SQL, Python, Data Analysis, Excel',                         10.0,   92000),
    ('Data Analyst',            'TCS',           'SQL, Data Analysis, Python, Excel',                         7.0,   64400),
    ('Data Analyst',            'Deloitte',     'SQL, Python, Data Analysis, Visualization',                  9.0,   82800),
    ('Data Analyst',            'Accenture',    'SQL, Data Analysis, Python, Pandas',                         8.0,   73600),

    # Software Engineer
    ('Software Engineer',       'Google',       'Python, Data Structures, SQL, System Design',               20.0,  184000),
    ('Software Engineer',       'Amazon',       'Java, Data Structures, SQL, System Design',                 22.0,  202400),
    ('Software Engineer',       'Microsoft',    'Python, Java, Data Structures, SQL',                        18.0,  165600),
    ('Software Engineer',       'TCS',          'Java, SQL, Data Structures, OOP',                            7.0,   64400),
    ('Software Engineer',       'Infosys',      'Java, Python, SQL, OOP',                                     6.5,   59800),
    ('Software Engineer',       'Wipro',        'Python, Java, SQL, Data Structures',                         6.0,   55200),

    # Web Developer
    ('Web Developer',           'Flipkart',     'HTML, CSS, JavaScript, React, SQL',                          9.0,   82800),
    ('Web Developer',           'Zomato',       'HTML, CSS, JavaScript, React, Python',                      10.0,   92000),
    ('Web Developer',           'Startup',      'HTML, CSS, JavaScript, React',                               7.0,   64400),
    ('Web Developer',           'Infosys',      'HTML, CSS, JavaScript, PHP, MySQL',                          6.0,   55200),
    ('Web Developer',           'TCS',          'HTML, CSS, JavaScript, PHP, SQL',                            5.5,   50600),

    # Backend Engineer
    ('Backend Engineer',        'Netflix',      'Python, Django, REST API, SQL, System Design',              28.0,  257600),
    ('Backend Engineer',        'Zomato',       'Python, Django, MySQL, REST API',                           12.0,  110400),
    ('Backend Engineer',        'Flipkart',     'Java, Python, MySQL, REST API, Docker',                     15.0,  138000),
    ('Backend Engineer',        'Startup',      'Python, Django, SQL, REST API',                             10.0,   92000),

    # Django Developer
    ('Django Developer',        'Zomato',       'Python, Django, MySQL, REST API, HTML',                     10.0,   92000),
    ('Django Developer',        'Startup',      'Python, Django, SQL, REST API',                              8.0,   73600),
    ('Django Developer',        'TCS',          'Python, Django, MySQL, HTML, CSS',                           7.0,   64400),

    # Cloud Engineer
    ('Cloud Engineer',          'Amazon',       'AWS, Cloud Computing, Python, Docker',                      22.0,  202400),
    ('Cloud Engineer',          'Microsoft',    'Azure, Cloud Computing, Python, Docker',                    20.0,  184000),
    ('Cloud Engineer',          'Google',       'GCP, Cloud Computing, Python, Kubernetes',                  24.0,  220800),
    ('Cloud Engineer',          'IBM',          'AWS, Cloud Computing, Docker, Linux',                       15.0,  138000),

    # Database / SQL
    ('Database Administrator',  'Oracle',       'SQL, MySQL, PostgreSQL, Database Design',                   12.0,  110400),
    ('Database Administrator',  'TCS',          'SQL, MySQL, Database Design, Python',                        8.0,   73600),

    # PHP Developer
    ('PHP Developer',           'Infosys',      'PHP, MySQL, HTML, CSS, JavaScript',                          6.0,   55200),
    ('PHP Developer',           'TCS',          'PHP, MySQL, HTML, CSS, SQL',                                  5.5,   50600),
    ('PHP Developer',           'Startup',      'PHP, MySQL, HTML, CSS, JavaScript',                           7.0,   64400),

    # AI Engineer
    ('AI Engineer',             'Google',       'Python, Machine Learning, Deep Learning, TensorFlow, NLP', 30.0,  276000),
    ('AI Engineer',             'Microsoft',    'Python, Machine Learning, Deep Learning, PyTorch',          28.0,  257600),
    ('AI Engineer',             'Startup',      'Python, Machine Learning, NLP, TensorFlow',                 18.0,  165600),

    # Blockchain
    ('Blockchain Developer',    'Infosys',      'Solidity, Blockchain, Smart Contracts, Python',             18.0,  165600),
    ('Blockchain Developer',    'Startup',      'Solidity, Blockchain, Ethereum, JavaScript',                16.0,  147200),

    # NLP
    ('NLP Engineer',            'Google',       'Python, NLP, Machine Learning, TensorFlow, Deep Learning', 26.0,  239200),
    ('NLP Engineer',            'Amazon',       'Python, NLP, Machine Learning, PyTorch',                   24.0,  220800),
]


class Command(BaseCommand):
    help = 'Seed realistic job listings into the database'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true',
                            help='Clear existing jobs before seeding')

    def handle(self, *args, **options):
        if options['clear']:
            count = JobListing.objects.count()
            JobListing.objects.all().delete()
            self.stdout.write(f'Cleared {count} existing jobs.')

        created = 0
        skipped = 0

        for title, company, skills, salary_lpa, salary_rupees in JOBS:
            _, was_created = JobListing.objects.get_or_create(
                job_title=title,
                company=company,
                defaults={
                    'skills_required': skills,
                    'salary_lpa':      salary_lpa,
                    'salary_rupees':   salary_rupees,
                }
            )
            if was_created:
                created += 1
            else:
                skipped += 1

        self.stdout.write(self.style.SUCCESS(
            f'Done! Created: {created}, Skipped: {skipped}'
        ))
        self.stdout.write(self.style.SUCCESS(
            f'Total jobs in DB: {JobListing.objects.count()}'
        ))