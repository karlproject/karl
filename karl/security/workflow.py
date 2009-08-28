from repoze.bfg.security import has_permission
from repoze.bfg.traversal import model_path
from repoze.folder.interfaces import IFolder
from repoze.lemonade.interfaces import IContent
from repoze.lemonade.content import get_content_type
from repoze.workflow import get_workflow
from repoze.workflow.statemachine import StateMachine
from repoze.workflow.statemachine import StateMachineError

from karl.security.policy import ALL

_marker = object()

class SecuredStateMachine(StateMachine):
    def add(self, state, transition_id, newstate, transition_fn, **kw):
        if not 'permission' in kw:
            kw['permission'] = None
        return StateMachine.add(self, state, transition_id, newstate,
                                transition_fn, **kw)

    def secured_execute(self, context, request, transition_id):
        state = getattr(context, self.state_attr, _marker) 
        if state is _marker:
            state = self.initial_state
        si = (state, transition_id)
        sn = (state, None)
        newstate = None
        # exact state match?
        if si in self.states:
            newstate, transition_fn, kw = self.states[si]
        # no exact match, how about a None (catch-all) match?
        elif sn in self.states:
            newstate, transition_fn, kw = self.states[sn]
        if newstate is None:
            raise StateMachineError(
                'No transition from %r using transition %r'
                    % (state, transition_id))
        permission = kw['permission']
        if request is not None and permission is not None:
            if not has_permission(permission, context, request):
                raise StateMachineError(
                    '%s permission required for transition %r' % (
                    permission, transition_id)
                    )
        self.before_transition(state, newstate, transition_id, context, **kw)
        transition_fn(state, newstate, transition_id, context, **kw)
        self.after_transition(state, newstate, transition_id, context, **kw)
        setattr(context, self.state_attr, newstate)

    def secured_transition_info(self, context, request, from_state=None):
        info = StateMachine.transition_info(self, context, from_state)
        return [ thing for thing in info if
                 has_permission(thing['permission'], context, request) ]


def reset_security_workflow(root, output=None):
    count = 0
    for node in postorder(root):
        if IContent.providedBy(node):
            if has_custom_acl(node):
                continue # don't mess with objects customized via edit_acl
            content_type = get_content_type(node)
            workflow = get_workflow(content_type, 'security', node)
            if workflow is not None:
                try:
                    state, msg = workflow.reset(node)
                except:
                    if output is not None:
                        output('Error while resetting %s' % model_path(node))
                    raise
                if output is not None:
                    if msg:
                        output(msg)
                count += 1
    if output is not None:
        output('updated %d content objects' % count)

def postorder(startnode):
    def visit(node):
        if IFolder.providedBy(node):
            for child in node.values():
                for result in visit(child):
                    yield result
                    # attempt to not run out of memory
        yield node
        if hasattr(node, '_p_deactivate'):
            node._p_deactivate()
    return visit(startnode)

def has_custom_acl(ob):
    if hasattr(ob, '__custom_acl__'):
        if getattr(ob, '__acl__', None) == ob.__custom_acl__:
            return True
    return False

def get_security_states(workflow, context, request):
    if has_custom_acl(context):
        return []
    states = workflow.state_info(context, request)
    # if there's only one state, hide the state widget
    if len(states) == 1:
        return []
    return states
    
def ace_repr(ace):
    action = ace[0]
    principal = ace[1]
    permissions = ace[2]
    if not hasattr(permissions, '__iter__'):
        permissions = [permissions]
    if permissions == ALL:
        permissions = ['ALL']
    permissions = sorted(list(set(permissions)))
    return '%s %s %s' % (action, principal, ', '.join(permissions))

def acl_diff(ob, acl):
    ob_acl = getattr(ob, '__acl__', {})
    if ob_acl != acl:
        added = []
        removed = []
        for ob_ace in ob_acl:
            if ob_ace not in acl:
                removed.append(ace_repr(ob_ace))
        for ace in acl:
            if ace not in ob_acl:
                added.append(ace_repr(ace))
        return '|'.join(added), '|'.join(removed)
    return None, None

