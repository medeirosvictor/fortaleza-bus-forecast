.PHONY: data clean-data

data: model-data/2015/top100_lines_2015.csv

model-data/2015/top100_lines_2015.csv: model-data/data.zip
	@echo "Extracting model-ready datasets..."
	cd model-data && unzip -o data.zip
	mkdir -p model-data/2015 model-data/2018 model-data/2020
	mv -f model-data/top100_lines_2015.csv model-data/2015/
	mv -f model-data/top100_lines_2018.csv model-data/2018/
	mv -f model-data/top100_lines_2020.csv model-data/2020/
	@echo "Done. CSVs extracted to model-data/{2015,2018,2020}/"

clean-data:
	rm -f model-data/2015/*.csv model-data/2018/*.csv model-data/2020/*.csv
