### Makefile --- 

## Author: shell@dsk.lan
## Version: $Id: Makefile,v 0.0 2014/07/16 13:44:42 shell Exp $
## Keywords: 
## X-URL: 

build:
	find . -name '*.md' -exec ~/bin/md2slide {} \;

clean:
	find . -name '*.html' -delete

### Makefile ends here
