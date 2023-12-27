from autoscraper import AutoScraper

url = 'https://www.britannica.com/place/Milky-Way-Galaxy'

# We can add one or multiple candidates here.
# You can also put urls here to retrieve urls.
wanted_list = ["Mars","NASA"]

scraper = AutoScraper()
result = scraper.build(url, wanted_list)
print(result)