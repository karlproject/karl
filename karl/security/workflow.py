from repoze.bfg.security import has_permission
from repoze.workflow.statemachine import StateMachine
from repoze.workflow.statemachine import StateMachineError

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

