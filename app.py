from flask import Flask, render_template, request
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
import requests, json
from pymongo import MongoClient
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.image as img
import base64
from io import BytesIO
from matplotlib.figure import Figure

# from pyspark.sql import SparkSession
# from pyspark.sql.types import StructType

# https://pymongo.readthedocs.io/en/stable/tutorial.html
# https://matplotlib.org/
app = Flask(__name__)


@app.route("/")
def main():  # put application's code here
    client = MongoClient('mongodb://localhost:27017/')
    all_death = client['death']['death_data']

    years = all_death.find().distinct("Year")
    country = all_death.find().distinct("Entity")

    return render_template('index.html', country=country, year=years)


@app.route("/plot", methods=['POST'])
def plot():
    data = []
    if request.method == 'POST':
        year = request.form['year']
        year = int(year)
        client = MongoClient('mongodb://localhost:27017/')
        all_death = client['death']['death_data']
        # print(year)
        lis = ["Executions", "Meningitis", "Alzheimer", "Parkinson", "Nutritional_deficiencies", "Malaria", "Drowning",
               "Interpersonal_violence", "Maternal_disorders", "HIV/AIDS", "Drug_use_disorders", "Tuberculosis",
               "Cardiovascular_diseases", "Lower_respiratory_infections", "Neonatal_disorders", "Alcohol_use_disorders",
               "Self-harm", "Exposure_to_forces_of_nature", "Diarrheal", "Environmental_heat_and_cold_exposure",
               "Neoplasms", "Conflict_and_terrorism", "Diabetes_mellitus", "Chronic_kidney", "Poisonings",
               "Protein-energy_malnutrition", "Terrorism", "Road_injuries", "Chronic_respiratory",
               "Cirrhosis_and_other_chronic" "liver", "Digestive", "Fire_heat_and_hot_substances", "Acute_hepatitis"]
        req = {}
        for el in lis:
            req[el] = {"$sum": f"${el}"}
        req["_id"] = "$Year"
        print(req)
        el = all_death.aggregate([
            {'$match': {'Year': year}},
            {'$group' : req}
        ])

        for i in el:
            del i['_id']
            print(i)
            data.append(i)
        print(data)

    return render_template("sum_per_year.html", data=data, headers=lis)

#plotly
@app.route('/death', methods=['POST', 'GET'])
def death():
    client = MongoClient('mongodb://localhost:27017/')
    if request.method == 'POST':
        year = request.form['year']
        country = request.form['country']

        client = MongoClient('mongodb://localhost:27017/')
        all_death = client['death']['death_data']
        print(year, country)
        el = all_death.find_one({"Year": int(year), "Entity": country})
        if el is None:
            return "No data for this year and country"
        data = el
        del el['_id']
        del el['Year']
        del el['Entity']
        if 'Code' in el.keys():
            del el['Code']
        names = el.keys()
        values = el.values()
        fig, ax = plt.subplots()
        ax.bar(names, values, label="death")
        ax.legend()
        for tick in ax.get_xticklabels():
            tick.set_rotation(55)
        plt.savefig("static/img/death_per_country.jpg")
        return render_template("death.html", data=data)


@app.route('/death/<year>/<country>')
def death_per_url(year, country):
    client = MongoClient('mongodb://localhost:27017/')
    with open("annual-number-of-deaths-by-country-and-year.json", "r") as f:
        data = json.load(f)
        country = country.title()
        return render_template("death.html", data=data[year][country])


@app.route('/stats/', methods=['POST', 'GET'])
def stats():
    client = MongoClient('mongodb://localhost:27017/')
    if request.method == 'POST':
        country = request.form['country']
        all_death = client['death']['death_data']
        el = all_death.find({"Entity": country})
        data = []
        for i in el:
            if '_id' in i.keys():
                del i['_id']
            if 'Entity' in i.keys():
                del i['Entity']
            if 'Code' in i.keys():
                del i['Code']
            data.append(i)

        df = pd.DataFrame(data)
        print(df)
        df.plot(x='Year', kind='line', figsize=(10, 5), legend=False)

        plt.savefig("static/img/map.jpg")
    return render_template("death_per_entity.html")


@app.route('/test')
def test():
    print("test")
    # client = MongoClient('mongodb://localhost:27017/')


@app.route('/agg', methods=['POST', 'GET'])
def agg():
    client = MongoClient('mongodb://localhost:27017/')
    all_death = client['death']['death_data']
    el = all_death.find_one({"Year": int(2007), "Entity": "France"})
    if el is None:
        return "No data for this year and country"
    data = el
    del el['_id']
    del el['Year']
    del el['Entity']
    if 'Code' in el.keys():
        del el['Code']
    names = el.keys()
    if request.method == 'POST':
        data = []
        for name in names:
            if name in list(request.form.keys()):
                data.append(name)
        data = [f"${el}" for el in data]
        all_death = client['death']['death_data']
        el = all_death.find({}, {"Entity": 1, "Year": 1, "total": {"$add": data}})
        dict_el = []
        for i in el:
            dict_el.append(i)
    return render_template("sum.html", data=dict_el)


@app.route('/ck')
def displayceckbox():
    client = MongoClient('mongodb://localhost:27017/')
    all_death = client['death']['death_data']
    el = all_death.find_one({"Year": int(2007), "Entity": "France"})
    if el is None:
        return "No data for this year and country"
    data = el
    del el['_id']
    del el['Year']
    del el['Entity']
    if 'Code' in el.keys():
        del el['Code']
    names = el.keys()
    fields = names
    return render_template('ckb.html', data={'fields': fields})


if __name__ == '__main__':
    app.run()
