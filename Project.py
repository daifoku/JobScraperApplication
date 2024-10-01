import requests
from bs4 import BeautifulSoup
import csv
import matplotlib.pyplot as plt

# Job class, holds job information
class Job:
    # Constructor w/ args
    def __init__(self, title, company, location, description, posting_date, deadline, job_type, qualifications):
        self.title = title
        self.company = company
        self.location = location
        self.description = description
        self.posting_date = posting_date
        self.deadline = deadline
        self.job_type = job_type
        self.qualifications = qualifications

    def __repr__(self):
        return f"Job(title={self.title}, company={self.company}, location={self.location})"

  
    # __repr__ method is intended to provide a detailed, unambiguous string representation of an object. 
    # It's mainly for developers to understand what the object contains or represents.
  
    def __repr__(self):
        return f"Job(title={self.title}, company ={self.company}, link={self.link})"
    
    # display job info
    def display_info(self):
        print(f"Job Title: {self.title}")
        print(f"Link: {self.link}")
        print(f"Description: {self.description}")


# Scraper class - Responsible for sending requests and fetching HTML content - Handles Pagination
class Scraper:
    def __init__(self, base_url):
        self.base_url = base_url # Store the base URL


    def fetch_page(self, page_number=1):
        url = f"{self.base_url}?page={page_number}" # Constructs the URL with the given page number (for pagination).

        # Sends an HTTP GET request to fetch the page content.
        response = requests.get(url)

        # gives you the HTTP status code of the response (e.g., 200 means OK, 404 means the page was not found)
        if response.status_code == 200: 
            return response.content
        else:
            raise Exception(f"Failed to retrieve webpage. Status code: {response.status_code}")
    
    def fetch_all_pages(self, max_pages=5):  # Set max_pages or determine how to detect last page dynamically
        pages_content = []
        for page in range(1, max_pages+1):
            try:
                content = self.fetch_page(page)
                pages_content.append(content)
            except Exception as e:
                print(f"Error fetching page {page}: {e}")
                break  # Stop if an error occurs
        return pages_content


# JobParser Class - Responsible for parsing the page and extracting job data
class JobParser:
    def __init__(self, html_content):
        # Parse the HTML content using BeautifulSoup and store it in self.soup for later use
        self.soup = BeautifulSoup(html_content, 'html.parser')

    def extract_jobs(self):
        jobs = []
        # Locate the job-posting block
        job_listing = self.soup.find('div', class_='job-preview')

        # Extract the job title
        title_tag = job_listing.find('h1', class_='sc-jmHipa')
        title = title_tag.text.strip() if title_tag else 'N/A'

        # Extract the company name
        company_tag = job_listing.find('div', class_='sc-jPipnV')
        company = company_tag.text.strip() if company_tag else 'N/A'

        # Extract location (it's in the 'Onsite' div)
        location_tag = job_listing.find('div', string=lambda text: 'Onsite' in text)
        location = location_tag.text.strip() if location_tag else 'N/A'

        # Extract the job description from the <p> tags within the description
        description_tag = job_listing.find('div', class_='sc-cZWPfn').find('p')
        description = description_tag.get_text(separator=' ').strip() if description_tag else 'N/A'

        # Extract the posting date and deadline
        posted_info = job_listing.find('div', class_='sc-fNALa').text
        posted_date, deadline = posted_info.split('∙')

        # Extract job type and any qualification
        job_type = job_listing.find('div', string=lambda text: 'Cooperative' in text)
        qualifications = job_listing.find_all('li')

        # List of qualifications or skills extracted from the list
        qualifications_list = [q.text.strip() for q in qualifications] if qualifications else []

        # Create the Job object and append to list
        job = Job(title, company, location, description, posted_date.strip(), deadline.strip(), job_type.text.strip(), qualifications_list)
        jobs.append(job)

        return jobs

# DataProcessor Class - Cleans, processes, and analyzes the data
class DataProcessor:
    def __init__(self, jobs):
        self.jobs = jobs

    def save_to_csv(self, filename):
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Job Title', 'Company', 'Link', 'Description'])
            for job in self.jobs:
                writer.writerow([job.title, job.company, job.link, job.description])
    
    def extract_common_skills(self):
        skill_count = {}
        common_skills = ['Python', 'Java', 'SQL', 'C', 'C++', 'React', 'teamwork', 'communication'] # extend list
        for job in self.jobs:
            for skill in common_skills:
                if skill.lower() in job.description.lower():
                    skill_count[skill] = skill_count.get(skill, 0) + 1
        return skill_count 


# Visualizer Class - Responsible for visualizing the data
class Visualizer:
    def __init__(self, jobs):
        self.jobs = jobs

    def visualize_keywords(self, skill_count):
        # Bar chart of skills
        skills = list(skill_count.keys())
        counts = list(skill_count.values())
        plt.bar(skills, counts)
        plt.xlabel('Skills')
        plt.ylabel('Count')
        plt.title('Most Common Job Skills')
        plt.show()


# Bringing it all together
class JobScraperApp:
    def __init__(self, url):
        self.scraper = Scraper(url)

    def run(self):
        html_pages = self.scraper.fetch_all_pages(max_pages=5)  # Scrape multiple pages
        all_jobs = []
        for page_content in html_pages:
            parser = JobParser(page_content)
            jobs = parser.extract_jobs()
            all_jobs.extend(jobs)

        processor = DataProcessor(all_jobs)
        processor.save_to_csv('jobs.csv')

        visualizer = Visualizer(all_jobs) # Visualize the data
        visualizer.visualize_keywords()

# Running the program
if __name__ == "__main__":
    url = 'https://example.com/jobs'  # Replace with your target job page
    app = JobScraperApp(url)
    app.run()