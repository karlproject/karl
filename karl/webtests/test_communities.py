from karl.webtests.base import Base

# Help on the 72 char limit
dc = '/communities/default'

class TestCommunitiesView(Base):

    def test_it(self):
        # After login you'll be at the Default Community home page
        self.login()

        # communities_view, active and all
        response = self.app.get('/communities/active_communities.html')
        self.assertTrue('KARL Communities' in response)
        response = self.app.get('/communities/all_communities.html')
        self.assertTrue('KARL Communities' in response)

        # wiki_index
        response = self.app.get(dc + '/wiki/wikitoc.html')
        self.assertTrue('Wiki Index' in response)
