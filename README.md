# Interlinking Schema.org Knowledge Fragments using Side Information

This project aims to make it easy to condense large-scale interlinking of a forest of RDF Schema.org dumps into tractable files, in bounded memory and computational cycles.

Usage
-----

**Example Usage**

    $python processData.py --input /Interlinking-Schema.org/data/2017/schema_Library.gz --output /Interlinking-Schema.org/results/ --type http://schema.org/Library --prop1 name --prop2 address --prop3 email --identifier telephone --year 2017 --num_query 20000 --num_batch 20

Example dump data and (2017 schema_Library.gz) and processed data are respectively in data/2017 and results.

**--input**:  *absolute file path and name of input schema.org dump (.gz).*
**--output**: *a folder to save the result files*
**--type**: *target schema.org type*
**--prop1-3*: *schema.org properties to include (e.g., "name", "address", "email", "title")*
**--identifier*: *identifier property which can be unique for each entity (e.g., "telephone", "isbn")*
**--num_rdf*: *number of RDFs tha will be condensed in one file*
**--num_batch*: *number of result files that are processed together*

Requirements
------------
* urlparse
* phonenumbers