rm -rf UNZIPPED/ccmt TEST_DATA/OUT/ccmt; python ccviz.py TEST_DATA/crashes/ccmt/164.125.34.86_2019-10-18-15-25-13.zip -o TEST_DATA/OUT/ccmt
echo -----------------------------------------
echo test 1 ccmt passed?
rm -rf UNZIPPED/1019_Ext TEST_DATA/OUT/1019_Ext; python ccviz.py TEST_DATA/crashes/1019_Ext/164.125.34.86_2019-10-19-20-37-01.zip -o TEST_DATA/OUT/1019_Ext
echo -----------------------------------------
echo test 2 Ext passed?
rm -rf UNZIPPED/ TEST_DATA/OUT/1019_Big_P5xP8; python ccviz.py TEST_DATA/crashes/1019_Big_P5xP8/164.125.34.86_2019-10-19-15-13-21.zip -o TEST_DATA/OUT/1019_Big_P5xP8
echo -----------------------------------------
echo test 3 Big passed?
