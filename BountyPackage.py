import json

from StaticSearch import get_country_info_v2, get_batch_core_data, get_core_data

class Bounty:
  def __init__(self, name, size, price, country, currency, user, id, slug, img):
    self.name = name
    self.size = size
    self.target_price = price
    self.country = country
    self.currency = currency
    self.user = user
    self.id = id
    self.url = f"https://www.goat.com/sneakers/{slug}"
    self.img = img

  def check_validity(self, scraper):
    rate = get_country_info_v2(scraper, self.country)
    output = scraper.get(f"https://www.goat.com/web-api/v1/products/search?productTemplateId={self.id}&shoeCondition=used&size={self.size}&sortBy=size&countryCode={self.country}")
    shoes = json.loads(output.text)
    for shoe in shoes['products']:
      if 5 + self.target_price >= round((shoe['priceCents'] / 100) * rate, 2):
        return [self.url]
    return []

  def returnType(self):
    return 'One-time Bounty'

  def returnUser(self):
    return self.user
  
  def __str__(self):
    name = f"Name: {self.name}\n"
    size = f"Size: {self.size}\n"
    price = f"Price: {self.target_price} {self.currency}\n"
    status = f"Status: {self.returnType()}"
    return name + size + price + status

####
class PermaBounty(Bounty):
  def __init__(self, name, size, price, country, currency, user, id, slug, img):
    super().__init__(name, size, price, country, currency, user, id, slug, img)
    self.items = []

  def check_validity(self, scraper):
    rate = get_country_info_v2(scraper, self.country)
    output = scraper.get(f"https://www.goat.com/web-api/v1/products/search?productTemplateId={self.id}&shoeCondition=used&size={self.size}&sortBy=size&countryCode={self.country}")
    shoes = json.loads(output.text)
    for shoe in shoes['products']:
      if 5 + self.target_price >= round((shoe['priceCents'] / 100) * rate, 2): 
        if shoe['id'] not in self.items:
          self.items.append(shoe['id'])
          return [self.url]
    return []
  
  def returnType(self):
    return 'PermaBounty'
###
class BatchBounty(PermaBounty):
    def __init__(self, name, size, price, country, currency, user):
        super().__init__(name, size, price, country, currency, user, 0, 0, 0) 
    
    def check_validity(self, scraper):
        shoe_list = get_batch_core_data(scraper, self.name)
        available_shoes = []
        for shoe_name in shoe_list:
            id, slug, value, img = get_core_data(scraper, shoe_name)
            rate = get_country_info_v2(scraper, self.country)
            output = scraper.get(f"https://www.goat.com/web-api/v1/products/search?productTemplateId={id}&shoeCondition=used&size={self.size}&sortBy=size&countryCode={self.country}")
            shoes = json.loads(output.text)
            for shoe in shoes['products']:
                if 5 + self.target_price >= round((shoe['priceCents'] / 100) * rate, 2): 
                    if shoe['id'] not in self.items:
                        self.items.append(shoe['id'])
                        available_shoes.append((value, f"https://www.goat.com/sneakers/{slug}"))
        return available_shoes
        
    def returnType(self):
        return 'BatchBounty'

####
class BountyBoard:
  def __init__(self):
    self._bounties = []
    self._length = 0
    self._completedBounties = 0
  
  def add_bounty(self, bounty):
    self._bounties.append(bounty)
    self._length += 1

  def remove_bounty_at_index(self, user, choiceIndex, clearAll=False):
    index=0
    for bounty in self._bounties:
      if bounty.returnUser() == user and (index == choiceIndex or clearAll):
        self._length -= 1
        self._bounties.remove(bounty)
        return True
      index += 1
    return False
    
  def remove_bounty(self, bounty):
    self._bounties.remove(bounty)
    self._length -= 1

  def totalWipe(self):
    self._bounties.clear()
    self._length = 0
    self._completedBounties = 0
  
  def getCompletedBounties(self):
    return self._completedBounties

  def updateCompletedBounties(self):
    self._completedBounties += 1

  def getLength(self):
    return self._length

  def get_user_bounties(self, user):
    string = '----------\n'
    index = 0
    for i in self._bounties:
      if i.returnUser() == user:
        string+=f'ID: {index}\n'
        string+=str(i)+"\n"
        string+='----------\n'
        index += 1
    if string == '----------\n':
      string += 'Empty'
    return string 
    
  def check_bounties(self, scraper):
    arr = []
    for i in reversed(self._bounties):
        temp = i.check_validity(scraper)
        if temp != []:
            for j in temp: 
                name = i.name if i.returnType() != "BatchBounty" else j[0]
                link = i.name if i.returnType() != "BatchBounty" else j[1]
                arr.append({
                    'Bounty Data':[name, link],       
                    'User':i.user, 
                    'Price':f"{i.target_price} {i.currency}",
                    'Size':i.size
                })
        if i.returnType() == 'One-time Bounty':
          self.remove_bounty(i)
    return arr
      
  def __len__(self):
    return self._length
  
  def __str__(self):
    string = '----------\n'
    if len(self._bounties) == 0:
      return string + 'Empty'
    for index, i in enumerate(self._bounties):
      string+=f'Relative ID: {index}\n'
      string+=str(i)+"\n"
      string+='----------\n'
    return string 
