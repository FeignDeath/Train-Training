% get the chain of timesteps
at(V,A,T) :- dl((A,V),T).
next(A,T,T') :- at(V,A,T), at(V',A,T'), V!=V', T<T', V=VBetween: at(VBetween,A,T+1..T'-1).

% implement the actions
% if a train traverses an edge to which takes 5 timesteps to traverse and hast 10 timesteps of time it should:
    % 0 turn correctly
    % 1-3 move forward
    % 4-8 wait
    % 9 move forward
% turn correctly
a(A,O,T) :- next(A,T,T'), at(U,A,T), at(V,A,T'), turn(wedge(U,V,_),O).
a(A,2,T) :- next(A,T,T'), at(U,A,T), at(V,A,T'), not turn(wedge(U,V,_),_), U != vertex(start).
% move forward
a(A,2,T+1..T+N-2) :- next(A,T,T'), at(U,A,T), at(V,A,T'), wedge(U,V,N).
% wait for the leftover time
a(A,4,T+N-1..T'-2) :- next(A,T,T'), at(U,A,T), at(V,A,T'), wedge(U,V,N).
% last move
a(A,2,T'-1) :- next(A,T,T'), at(U,A,T), at(V,A,T'), wedge(U,V,N), N>1.

% start handling
a(A,4,T..T'-2) :- at(vertex(start),A,T), next(A,T,T').
a(A,2,T'-1) :- at(vertex(start),A,T), next(A,T,T').

% translate all actions into the ouput
output(1,move_left).output(2,move_forward).output(3,move_right).output(4,wait).
action(train(A),O',T) :- a(A,O,T), output(O,O').

% safety constraint to see whether I messed something up
:- a(A,O,T), a(A,O',T), O>O'.

#show action/3.