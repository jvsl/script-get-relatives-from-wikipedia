from bs4 import BeautifulSoup as bs
import requests
import json

relations = ('Cônjuge', 'Filhos', 'Filho', 'Filha', 'Filhas', 'Filiação', 'Irmãos', 'Esposa', 'Marido', 'Progenitores',
             'Primeira-dama', 'Irmãs', 'Avós')

url_wikipedia = 'https://pt.wikipedia.org/wiki/{}'
google_search_page_query_url = 'https://www.google.com.br/search?q={}'
url_senators = 'http://legis.senado.leg.br/dadosabertos/senador/lista/atual'


def get_senators_names():
    senators = requests.get(url_senators, headers={'accept': 'application/json'})
    senators_json_list = senators.json()['ListaParlamentarEmExercicio']['Parlamentares']['Parlamentar']
    senators_names_list = []
    for name in senators_json_list:
        senators_names_list.append(name['IdentificacaoParlamentar']['NomeParlamentar'])
    return senators_names_list


def get_google_search_page_by_query(google_page_search_query):
    return requests.get(google_page_search_query)


def get_span_tag(senator_name):
    url = google_search_page_query_url.format(senator_name)
    soup = bs(get_google_search_page_by_query(url).text, 'lxml')
    div_tag = soup.find('div', {'class': '_uXc hp-xpdbox'})
    span_tag_list = div_tag.find_all('span', {'class': '_gS'})
    return span_tag_list


def get_information_family_from_google_wikipedia_page():
    senators_names = get_senators_names()
    relative_info = {}
    list_relations = {}
    all_senators = []
    list_errors = []

    for senator in senators_names:
        print (senator)
        try:
            span_tag_list = get_span_tag(senator)

            for span in span_tag_list:
                relative = span.text.replace(":", "").replace(" ", "")
                if relative in relations:
                    if not relative_info:
                        relative_info = {relative: span.next_sibling.text.split(',')}
                    else:
                        relative_info[relative] = span.next_sibling.text.split(',')

            if relative_info:
                list_relations[senator] = relative_info
                all_senators.append(list_relations)
                list_relations = {}
                relative_info = {}
            else:
                list_errors.append(senator)
        except AttributeError:
            list_errors.append(senator)
    return dict(senators=all_senators, errors=list_errors)


def download_page(url) :
    return requests.get(url)


def get_information_family_from_wikipedia_page(senator_name):
    list_errors = []
    relation_info = {}
    list_relation_info = {}
    all_senators = []
    for senator in senator_name:
        print (senator)
        senator = senator.replace(' ', "_")

        url = url_wikipedia.format(senator)
        soup = bs(download_page(url).text, 'lxml')
        info = soup.find('table', {'class':'infobox_v2'}) if soup else None

        if info:
            td_tag_content = info.find_all({'td'})
            for content in td_tag_content:
                if content.text in relations:
                    if not relation_info:
                        relation_info = {content.text: content.next_sibling.next_sibling.text}
                    else:
                        relation_info[content.text] = content.next_sibling.next_sibling.text

            if relation_info:
                list_relation_info[senator] = relation_info
                all_senators.append(list_relation_info)
                relation_info = {}
                list_relation_info = {}
            else:
                list_errors.append(senator)
        else:
            list_errors.append(senator)

    return dict(senators=all_senators, errors=list_errors)


def get_senators_relatives():
    senators_from_google_page = get_information_family_from_google_wikipedia_page()
    senatores_from_wikipedia_page = get_information_family_from_wikipedia_page(senators_from_google_page.get('errors'))

    senators_from_google_page.pop('errors')
    senators_from_google_page['errors'] = senatores_from_wikipedia_page['errors']

    senators_from_google_page['senators'].extend(senatores_from_wikipedia_page['senators'])

    print(senators_from_google_page)
    write_dict_in_a_file('data.txt', senators_from_google_page)

def write_dict_in_a_file(filename, data):
    with open(filename, 'w') as outfile:
        json.dump(data, outfile, ensure_ascii=False)

if __name__ == '__main__':
    get_senators_relatives()



