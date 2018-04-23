import lxml.html as html
import requests
import datetime

facilities = {}

class Facility:
    def __init__(self, name, address, last_data_date, active, unit):
        self.name = name
        self.address = address
        self.last_data = last_data_date
        self.active = active
        self.unit_id = unit

def load_facilities():
    #This would contain the sql for fetching facility data, and the latest facility output data for each.
    #For this example, one will simply be hardcoded.
    facilities['611'] = Facility('Mohawk Valley Solar', '6599 State Route 26, Rome, NY 13440', '04/08/2018', True, 972)

def scrape_facility(id, row):
    #This would scrape the facility page for relevant information, most importantly getting the unit ID necessary to request the csv
    #and the start date.
    #Because it's more or less the same as the body of the script in content, and because actually downloading the data for everything
    #would take a bit long for demo purposes, this method is unimplemented.
    facilities[id] = Facility('', '', '', False, 0)

def persist_facility(facility):
    #Where the SQL for saving the facilities would go. The last_data field is not persisted, because it is derived from the facility's data on load.
    pass

def persist_csv(csv, unit):
    #Where the SQL for saving the newly downloaded data would go. As the README mentions, data is saved without alteration.
    #The unit id is added to each row as an identifier, and unused columns are omitted.
    pass

if __name__ == '__main__':
    site = html.parse('http://dg.nyserda.ny.gov/facilities/index.cfm?Filter=Solar')
    rows = site.xpath('//tr[contains(td/a/@href,"details")]') # All rows that have a link to a facility's details
    today = datetime.date.today().strftime('%m/%d/%Y')

    load_facilities()

    for row in rows:
        id = row.xpath('td/a/@href')[0][len('details.cfm?facility='):] # Since all links share the prefix, a simple substring will get the id
        if id not in facilities:
            scrape_facility(id, row)
        
        facility = facilities[id]
        if facility.active:
            data = {
                'Unit': facility.unit_id,
                'Type': 'csv',
                'Interval': 'hourly',
                'StartDate': facility.last_data,
                'EndDate': today
            }

            csv_page = requests.post('http://dg.nyserda.ny.gov/reports/csvreport.cfm', data)
            csv_doc = html.fromstring(csv_page.text)
            csv = requests.get(csv_doc.xpath('//a[contains(@href,"csv_files")]/@href')[0]).text
            persist_csv(csv, facility.unit_id)

            if 'current' not in row.xpath('td[@align="center"]/text()')[2]:
                facility.active = False #Mark as inactive
        
        persist_facility(facility)





    


