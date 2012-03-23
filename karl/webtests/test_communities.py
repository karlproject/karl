from karl.webtests.base import Base


class TestCommunitiesView(Base):

    def test_it(self):
        # After login you'll be at the Default Community home page
        response = self.login()
        response = response.click('Communities')
        response = response.follow() # redirect to Active Communities
        self.assertTrue('Active' in response)
        self.assertTrue('Communities' in response)
