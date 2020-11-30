# Lesson 7 - Parsing and Manipulating Bibliographic Data

- creating the overall structure for our MEMEX on HDD
	1) using out bibliogaphical data, we algorithmically generate paths for each publication
	2) we create those paths
	3) we copy relevant data into those paths: 1) bibliographical record (bib); 2) PDF

Let's break it down into smaller steps:

- first of all, it will actually be easier of take a look at this task from another perspective.
	- we should start from a single publication, or, better, a single bibliographical record.
	- after we fugure out how to process a single publication, we will just need to figure out how to process all of them

- so, let's start with a single bib record:
	- (we have written a function before that creates a dictionary from every bib record (let's call it **loadBib()**); so let our function take such a single-record dictionary as its argument);
	- what will we need from our function (let's call it **processBibRecord()**)? it must do the following:
		- to generate a unique path for the publication
		- check if that path exists, if not: create it
		- save bib record into that folder
		- copy PDF to that folder
	- what do we need to consider:
		- we need a simple and transparent way to algorithmically generate all this data, which will ensure easy access, browsability, and overall transparensy of our approach. In order to achieve it, we can use *a single* element from each record to generate all necessary paths and filenames. Namely, the *citation key*.

	- **path:** our path will be a concatenation of the path to memex (for example, `./MEMEX_SANDBOX/data/`) and a subpath unique to each publication, which we can generate from the citation key.
		- for example, if the citation key is `SavantMuslims2017`, the publication path should be `/s/sa/SavantMuslims2017/`
		- the concatenated path thus will be: `./MEMEX_SANDBOX/data/s/sa/SavantMuslims2017/`
		- **NB:** it may be a good idea to have a small function that takes paths to memex and the citation key as its arguments and returns the final path (let's call it **generatePublPath()**).
	- now, that we have **the path**, we can check whether it exists, and, if not, create it
	- now, we have our path and the actual folder on HDD, it is easy-peasy-lemon-squeezy to save a bibliographical record and a PDF into that folder.
		- for the same considerations of machine-readability, we should use use the ciation key to name our files: for example, `SavantMuslims2017.bib` for our bibliographical record, and `SavantMuslims2017.pdf` for our PDF file.

- now, we have a function that does all that we need from a single record, we can write another function (let's call it **processAllRecords()**) that will
	- take the large bibliographivcal dictionary generated with **loadBib()** as its argument
	- loops through this dictionary, and processes each record with **processBibRecord()**.

