from zope.interface import Interface

class ISecurityWorkflow(Interface):

    def setInitialState(**kw):
        """ Put the object into the correct initial state.

        o 'kw', if passed, will be form variables from the constructor form.

        o Set the ACL accordingly.
        """

    def updateState(**kw):
        """ Update the object's state, based on form variables.

        o 'kw', if passed, will be form variables from an edit form.

        o Set the ACL accordingly.
        """
        

    def getStateMap():
        """ Return a map of form variables representing the object state.
        """

    def execute(transition_id):
        """ Move the object into a security state using 'transition_id'.

        o Set the ACL accordingly.
        """
