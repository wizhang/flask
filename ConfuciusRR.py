import xml.etree.ElementTree as ET
import json
import pysolr
from watson_developer_cloud.watson_developer_cloud_service import \
    WatsonDeveloperCloudService


class ConfuciusRetrieveAndRankV1(WatsonDeveloperCloudService):
    default_url = 'https://gateway.watsonplatform.net/retrieve-and-rank/api'

    def __init__(self, url=default_url, **kwargs):
        WatsonDeveloperCloudService.__init__(self, 'retrieve_and_rank', url,
                                             **kwargs)

    def list_solr_clusters(self):
        return self.request(method='GET', url='/v1/solr_clusters',
                            accept_json=True)

    def create_solr_cluster(self, cluster_name=None, cluster_size=None):
        if cluster_size:
            cluster_size = str(cluster_size)
        params = {'cluster_name': cluster_name, 'cluster_size': cluster_size}
        return self.request(method='POST', url='/v1/solr_clusters',
                            accept_json=True, json=params)

    def delete_solr_cluster(self, solr_cluster_id):
        return self.request(method='DELETE',
                            url='/v1/solr_clusters/{0}'.format(
                                solr_cluster_id),
                            accept_json=True)

    def get_solr_cluster_status(self, solr_cluster_id):
        return self.request(method='GET',
                            url='/v1/solr_clusters/{0}'.format(
                                solr_cluster_id),
                            accept_json=True)

    def list_configs(self, solr_cluster_id):
        return self.request(method='GET',
                            url='/v1/solr_clusters/{0}/config'.format(
                                solr_cluster_id), accept_json=True)

    # Need to test
    def create_config(self, solr_cluster_id, config_name, config):
        return self.request(method='POST',
                            url='/v1/solr_clusters/{0}/config/{1}'.format(
                                solr_cluster_id, config_name),
                            files={'body': config},
                            headers={'content-type': 'application/zip'},
                            accept_json=True)

    def delete_config(self, solr_cluster_id, config_name):
        return self.request(method='DELETE',
                            url='/v1/solr_clusters/{0}/config/{1}'.format(
                                solr_cluster_id, config_name),
                            accept_json=True)

    def get_config(self, solr_cluster_id, config_name):
        return self.request(method='GET',
                            url='/v1/solr_clusters/{0}/config/{1}'.format(
                                solr_cluster_id, config_name))

    def list_collections(self, solr_cluster_id):
        params = {'action': 'LIST', 'wt': 'json'}
        return self.request(method='GET',
                            url='/v1/solr_clusters/{0}/solr/admin/collections'
                            .format(solr_cluster_id),
                            params=params, accept_json=True)

    def create_collection(self, solr_cluster_id, collection_name, config_name):
        params = {'collection.configName': config_name,
                  'name': collection_name,
                  'action': 'CREATE', 'wt': 'json'}
        return self.request(method='POST',
                            url='/v1/solr_clusters/{0}/solr/admin/collections'
                            .format(solr_cluster_id),
                            params=params, accept_json=True)

    def delete_collection(self, solr_cluster_id, collection_name,
                          config_name=None):
        params = {'name': collection_name, 'action': 'DELETE', 'wt': 'json'}
        return self.request(method='POST',
                            url='/v1/solr_clusters/{0}/solr/admin/collections'
                            .format(solr_cluster_id),
                            params=params, accept_json=True)

    def get_pysolr_client(self, solr_cluster_id, collection_name):
        base_url = self.url.replace('https://',
                                    'https://' + self.username + ':' +
                                    self.password + '@')
        url = base_url + '/v1/solr_clusters/{0}/solr/{1}'.format(
            solr_cluster_id, collection_name)
        return pysolr.Solr(url)

    def create_ranker(self, training_data, name=None):
        data = None
        if name:
            data = {'training_metadata': json.dumps({'name': name})}
        return self.request(method='POST', url='/v1/rankers', accept_json=True,
                            files=[('training_data', training_data)],
                            data=data)

    def list_rankers(self):
        return self.request(method='GET', url='/v1/rankers', accept_json=True)

    def get_ranker_status(self, ranker_id):
        return self.request(method='GET',
                            url='/v1/rankers/{0}'.format(ranker_id),
                            accept_json=True)

    def rank(self, solr_cluster_id, ranker_id, ranker_name, question):
        #top_answers = 10
        #data = {'answers': + top_answers}
        url = '/v1/solr_clusters/'+solr_cluster_id+'/solr/'+ranker_name+'/fcselect?q='+question+'&ranker_id='+ranker_id
        #print(url)
        results = self.request(method='GET',url=url, accept_json=False)
        #The results has a memebre variable 'text', which contains teh results in form of an xml
        #Takes a string of xml that ranker returns, outputs a list of dictionaries describing each returned result
        
        root = ET.fromstring(results.text.encode('utf-8'))
        result = []

        for doc in root[1]:
            ans = doc[0][0].text.replace("'", '"').replace('\\xa0', ' ')
            #Code to remove some invalid char that might have sneaked in
            start = ans.index('<p>')
            end = ans.index('</p>')
            ans = ans[:start] + ans[start:end].replace('"','<dq>') + ans[end:]
            dic = {}
            dic['body'] = json.loads(ans)['answer']
            dic['id'] = doc[1].text
            dic['version'] = doc[2].text
            dic['score'] = doc[3].text
            dic['vector'] = doc[4].text
            dic['confidence'] = doc[5].text
    
            result.append(dic)

        return result

    def delete_ranker(self, ranker_id):
        return self.request(method='DELETE',
                            url='/v1/rankers/{0}'.format(ranker_id),
                            accept_json=True)
    def removeCharTags(self, text):
        return text.replace('<colon>', ':').replace('<percent>','%').replace('<dq>', '\"').replace('<sq>','\'')