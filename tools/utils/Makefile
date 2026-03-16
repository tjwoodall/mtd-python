
all: dad.html davs.html wavs.html mad.html mavs.html bpd.html
	./get-header-info.py dad.html bpd.html davs.html mad.html mavs.html wavs.html

dad.html: headers-root.html
	curl -o $@ https://developer.service.hmrc.gov.uk/guides/fraud-prevention/connection-method/desktop-app-direct/

davs.html: headers-root.html
	curl -o $@ https://developer.service.hmrc.gov.uk/guides/fraud-prevention/connection-method/desktop-app-via-server/

wavs.html: headers-root.html
	curl -o $@ https://developer.service.hmrc.gov.uk/guides/fraud-prevention/connection-method/web-app-via-server/

mad.html: headers-root.html
	curl -o $@ https://developer.service.hmrc.gov.uk/guides/fraud-prevention/connection-method/mobile-app-direct/

mavs.html: headers-root.html
	curl -o $@ https://developer.service.hmrc.gov.uk/guides/fraud-prevention/connection-method/mobile-app-via-server/

bpd.html: headers-root.html
	curl -o $@ https://developer.service.hmrc.gov.uk/guides/fraud-prevention/connection-method/batch-process-direct/


# There doesn't seem a good/reliable way of scraping the connection method pages from this :-(
headers-root.html:
	curl -o $@ https://developer.service.hmrc.gov.uk/guides/fraud-prevention/connection-method/



