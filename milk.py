#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import pandas as pd


class DataGenerator():

    def __init__(self):
        pass

    def make_companies_db(self):
        ''' Creates a JSON file from the embedded company data in the
        MilkRoundabout company.html file
        '''
        from settings import COMPANIES_JSON
        companies = json.loads(COMPANIES_JSON)

        fp = open('companies.json', 'w')

        json.dump(companies,
                  fp,
                  sort_keys=True,
                  indent=4,
                  separators=(',', ': '))

        fp.close()

        return companies

    def get_company(self, name, companies):
        ''' Return the descriptor object for the named company
        '''
        for company in companies:
            if company['name'] == name:
                return company

    def make_company_map(self, companies):
        ''' Make a dict from the company data
        '''
        company_names = map(lambda c: c['name'], companies)
        company_map = {}

        for name in company_names:
            company_map[name] = self.get_company(name, companies)

        return company_map

    def flatten_vacancies(self, vacancies):
        ''' If it is possible to 'flatten' the dict attributes of each
        job vacancy entry, do so.
        '''
        def flattened(v):
            ''' Given a job vacancy entry, flatten the dict attribs if
            possible.
            '''
            new_v = {}
            for (vk, vv) in v.items():
                if type(vv) is dict:
                    for (vvk, vvv) in vv.items():
                        new_v['.'.join([vk, vvk])] = vvv
                        print(new_v)
                else:
                    new_v[vk] = vv
            return new_v

        def flattened_list(vlist):
            ''' For each company's vacancy list, flatten out the attributes.
            '''
            return map(lambda v: flattened(v), vlist)

        return dict(map(lambda v: (v[0], flattened_list(v[1])),
                        vacancies.items()))

    def make_vacancies_db(self, cmap):
        ''' Create a JSON representation of all vacancies.
        '''
        '''
        vacancies = dict(map(lambda c: (c['name'],
                             dict(map(lambda v: (int(v['id']), v),
                                      c['job_vacancies']))),
                         cmap.values()))
        '''
        vacancies = dict(map(lambda c: (c['name'], c['job_vacancies']),
                         cmap.values()))

        vacancies = self.flatten_vacancies(vacancies)

        fp = open('vacancies.json', 'w')

        json.dump(vacancies,
                  fp,
                  sort_keys=True,
                  indent=4,
                  separators=(',', ': '))

        fp.close()

        return vacancies


class DataReader():

    def __init__(self):
        self.init_db()

    def init_db(self):
        ''' Read the companies and vacancy data from JSON files
        '''
        fp = open('companies.json', 'r')
        self.companies = json.load(fp)
        fp.close()
        fp = open('vacancies.json', 'r')
        self.vacancies = json.load(fp)
        fp.close()

    def get_companies(self):
        return self.companies

    def get_vacancies(self):
        return self.vacancies

    def get_vacancies_df(self):
        ''' Return vacancies as a Pandas dataframe
        '''
        vacancies = self.get_vacancies()
        dfs = dict(map(lambda vl: (vl[0], pd.DataFrame(vl[1])),
                       vacancies.items()))
        new_dfs = {}
        for dfk in dfs.keys():
            c = dfs[dfk]
            if c is not None and c.index is not None and 'id' in c.columns:
                c.index = c['id']
                c['company'] = dfk
                c['skills'] = c['skills'].map(lambda sk: pd.DataFrame(sk))
                new_dfs[dfk] = c

        return new_dfs

    def get_skills_df(self, vdfs):
        ''' Return the skills required as a Pandas DataFrame
        '''
        pieces = []
        for dfk in vdfs.keys():
            vdf = vdfs[dfk]
            for job in vdf.index:
                skills_df = vdf.ix[job]['skills']
                skills_df['job_id'] = job
                skills_df['company'] = dfk
                pieces.append(skills_df)
        skills_df = pd.concat(pieces)
        skills_df.index = range(len(skills_df))
        return skills_df

if __name__ == "__main__":
    ''' If invoked as a standalone program, generate the  companies and
    vacancy databases.
    '''
    dgen = DataGenerator()
    companies = dgen.make_companies_db()
    company_map = dgen.make_company_map(companies)
    vacancies = dgen.make_vacancies_db(company_map)
