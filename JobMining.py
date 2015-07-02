from bs4 import BeautifulSoup
from urllib.request import build_opener
import sys
import json
import traceback

def main():    
    pagestart = int(sys.argv[1]);
    pageend= int(sys.argv[2]);
    dirout= sys.argv[3];
    url = r'http://jobsearch.naukri.com/jobs-in-india-'
    url2 ='?ql=india&qs=f'
    outputfile = dirout+"\\tables_"+str(pagestart)+"_"+str(pageend)+".json";
    file = open(outputfile, 'w+')
    mylist = list()
    j=0   
    for i in range(pagestart,pageend):  
        temp = url+str(i)+url2;
        opener = build_opener()
        opener.addheaders = [('User-agent', 'Try/'+str(i)+".0")]
        response = opener.open(temp)
        soup = BeautifulSoup(response)
        for content in soup.find("form").findAll('a',attrs={"target":"_blank"}) :
            listingurl = content.get('href');
            openerurl = build_opener()
            responseurl = openerurl.open(listingurl)
            soupurl = None
            try:
                soupurl = BeautifulSoup(responseurl)
                DataMatrix = setjdRows(soupurl.findAll('div',attrs={"class":"jdRow"}))
                DataMatrix['jobTitle']=soupurl.find('h1',attrs={"class":"jobTitle"}).getText()  
                DataMatrix['date']  =str(soupurl.find('span',attrs={"class":"fr"})).split('span')[3][1:][:-2].split()   
                DataMatrix['url'] = listingurl 
                DataMatrix['company'] = str(soupurl.find('div',attrs={"class":"jobDet"})).split('span')[2][:-2][2:]
                
                if len(str(soupurl.find('div',attrs={"class":"jobDet"})).split('span')) >=7 :
                    DataMatrix['alias'] = str(soupurl.find('div',attrs={"class":"jobDet"})).split('span')[4][:-2][2:]
                    DataMatrix['location'] = str(soupurl.find('div',attrs={"class":"jobDet"})).split('span')[6][:-6][2:].split()  
                elif len(str(soupurl.find('div',attrs={"class":"jobDet"})).split('span')) >=4 :     
                    DataMatrix['location'] = str(soupurl.find('div',attrs={"class":"jobDet"})).split('span')[4][:-6][2:].split()   
                             
                if len(str(soupurl.find('span',attrs={"class":"fl"})).split('span')) >=4 & len(str(soupurl.find('span',attrs={"class":"fl"})).split('span')[3].split('to')) >= 2:
                    DataMatrix['experienceMin'] = str(soupurl.find('span',attrs={"class":"fl"})).split('span')[3].split('to')[0][2:]
                    DataMatrix['experienceMax'] = str(soupurl.find('span',attrs={"class":"fl"})).split('span')[3].split('to')[1][:-10]
                elif len(str(soupurl.find('span',attrs={"class":"fl"})).split('span')) >= 11 :
                    DataMatrix['openings'] = str(soupurl.find('span',attrs={"class":"fl"})).split('span')[11][:-2][1:] 
                    DataMatrix['salaryMin'] = str(soupurl.find('span',attrs={"class":"fl"})).split('span')[7][:-2][1:].strip().split('-')[0].split(' ')[1]  
                    DataMatrix['salaryMax'] = str(soupurl.find('span',attrs={"class":"fl"})).split('span')[7][:-2][1:].strip().split('-')[1].split(' ')[1]
                    DataMatrix['currency'] = str(soupurl.find('span',attrs={"class":"fl"})).split('span')[7][:-2][1:].strip().split('-')[0].split(' ')[0]
                    DataMatrix['salaryRate']= str(soupurl.find('span',attrs={"class":"fl"})).split('span')[7][:-2][1:].strip().split('-')[1].split(' ')[2] 
                elif len(str(soupurl.find('span',attrs={"class":"fl"})).split('span')) >= 7 :
                    if 'Opening' in str(soupurl.find('span',attrs={"class":"fl"})):
                        DataMatrix['opening'] = str(soupurl.find('span',attrs={"class":"fl"})).split('span')[7][:-2][1:]
                    else : 
                        DataMatrix['salaryMin'] = str(soupurl.find('span',attrs={"class":"fl"})).split('span')[7][:-2][1:].strip().split('-')[0].split(' ')[1] 
                        DataMatrix['salaryMax'] = str(soupurl.find('span',attrs={"class":"fl"})).split('span')[7][:-2][1:].strip().split('-')[1].split(' ')[1] 
                        DataMatrix['currency'] = str(soupurl.find('span',attrs={"class":"fl"})).split('span')[7][:-2][1:].strip().split('-')[0].split(' ')[0] 
                        DataMatrix['salaryRate']= str(soupurl.find('span',attrs={"class":"fl"})).split('span')[7][:-2][1:].strip().split('-')[1].split(' ')[2]
                t=postprocess(DataMatrix)        
                mylist.append(t)               
            except Exception as e:
                j=j+1
    print(j)           
    json.dump(mylist, file)
    file.close()
    
def postprocess(DataMatrix):
    if 'salaryMin' in DataMatrix:
        DataMatrix['salaryMin']= DataMatrix['salaryMin'].replace(",", "")
    if 'salaryMax' in DataMatrix:
        DataMatrix['salaryMax']=DataMatrix['salaryMax'].replace(",", "")
        return DataMatrix
    
def setjdRows(list):
    valuest =[x.find('p').text for x in list]
    keyst=[x.find('span').text[:-1] for x in list]
    dictA = dict(zip(keyst, valuest))
    if 'Keyskills' in keyst :
        r=keyst.index('Keyskills')      
        dictA.pop('Keyskills',None)
        skills=[x.text for x in list[r].findAll('em')]
        dictA['Key Skills'] = skills
    if 'Education' in keyst :
        dictA.pop('Education',None)
    if 'Salary' in keyst :
        dictA.pop('Salary',None)
    return dictA;
        
if __name__ == "__main__":
   main()