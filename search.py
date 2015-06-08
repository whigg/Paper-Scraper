import requests
import bibtexparser
from HTMLParser import HTMLParser

#testRequest = requests.get("http://inspirehep.net/search?ln=en&ln=en&p=find+eprint+1506.01386&of=hx&action_search=Search&sf=earliestdate&so=d&rm=&rg=25&sc=0")

class SpiresFormat():
#	formatRequestPrefix="&of="
	def __init__(self,name,format_string,record_tag):
		self.name=name
		self.format_string=format_string
		self.record_tag=record_tag

#	def formatRequest(self):
#		return self.formatRequestPrefix+self.formatString

spiresBibtex=SpiresFormat("bibtex","hx","pre")
spiresJson=SpiresFormat("json","recjson","")

class SpiresSearch():
	inspire_url="http://inspirehep.net/search?"

	def __init__(self,search_string,data_format=spiresBibtex,chunk_size=25,jump=1,
			static_options={"sf" : "earliestdate"}):

		self.chunk_size=chunk_size
		self.jump=jump
		self.data_format=data_format
		self.static_options=static_options
		self.search_string=search_string
		self.generate_request_string()

		self.parser=SpiresHTMLParser(data_format)
		self.requested_flag=False

	def update_options(self):
		self.search_options=self.static_options
		self.search_options["of"]=self.data_format.format_string
		self.search_options["rg"]=str(self.chunk_size)
		self.search_options["jrec"]=str(self.jump)

	def generate_request_string(self):
		# generates the actual spires search string 
		self.request_string=self.inspire_url+"&p="+self.search_string
		# adds the options, including the data format
		self.update_options()
		for key, value in self.search_options.items():
			self.request_string+="&"+key+"="+value



	def get_previous_chunk(self):
		if self.jump>self.chunk_size:
			self.jump-=self.chunk_size
		else:
			print "chunk size larger than offset. Resetting search to first chunk"
			self.jump=1
		self.perform_request()

	def get_next_chunk(self):
		self.jump+=self.chunk_size
		self.perform_request()
		
	def perform_request(self):
		self.generate_request_string()
		self.requested_flag=True
		self.request=requests.get(self.request_string)

	def parse_request(self):
		if not self.requested_flag:
			self.perform_request()
		return self.parser.get_tag_data(self.request.text)

class SpiresBibtexSearch(SpiresSearch):

	def __init__(self,search_string,chunk_size=25,jump=1,
			static_options={"sf" : "earliestdate"}):
		SpiresSearch.__init__(self,search_string,data_format=spiresBibtex,
					chunk_size=chunk_size,jump=jump,
					static_options=static_options)

class SpiresBibtexEprintSearch(SpiresBibtexSearch):
	def __init__(self,eprint_num):
		SpiresBibtexSearch.__init__(self,"find eprint+"+eprint_num)


class SpiresBibtexDoiSearch(SpiresBibtexSearch):
	def __init__(self,doi):
		SpiresBibtexSearch.__init__(self,"find doi+"+doi)
		

class SpiresHTMLParser(HTMLParser):
	def __init__(self,data_format):
		HTMLParser.__init__(self)
		self.pre_flag=False
		self.data_format=data_format
		self.record_tag=data_format.record_tag

	def get_tag_data(self,text):
		self.results=[]
		self.feed(text)
		return self.results

	def handle_starttag(self,tag,attrs):
		if tag==self.record_tag:
#			print "found start-tag "+tag
			self.pre_flag=True
	
	def handle_endtag(self,tag):
		if tag==self.record_tag:
#			print "found end-tag "+tag
			self.pre_flag=False

	def handle_data(self,data):
		if self.pre_flag:
			print "Found bibtex: "+data
			self.results.append(data)


#test_search=SpiresBibtexSearch("find+a+gardi")
test_search=SpiresBibtexEprintSearch("0709.2877")
