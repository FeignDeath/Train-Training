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
a(A,2,T'-1) :- next(A,T,T'), at(U,A,T), at(V,A,T'), wedge(U,V,N).

% start handling
a(A,4,T..T'-2) :- at(vertex(start),A,T), next(A,T,T').
a(A,2,T'-1) :- at(vertex(start),A,T), next(A,T,T').


% % reconstruct timestep path
% at(V,A,T) :- dl((A,V),T).

% % fill the gaps
% next(A,T,T') :- at(V,A,T), at(V',A,T'), V!=V', T<T', V=VBetween: at(VBetween,A,T+1..T'-1).
% at(V,A,C) :- at(V,A,T), next(A,T,T'), C=T+1..T'-1.

% % action given to start
% a(A,2,T) :- not at(vertex(start),A,T+1), at(vertex(start),A,T).
% % stop action if an agent waits
% a(A,4,T) :- at(V,A,T+1), at(V,A,T).
% % generate turns if necessary
% a(A,O,T) :- at(V,A,T), at(V',A,T+1), turn(edge(V,V'),O).
% % generate move action if a train continues moving
% a(A,2,T) :- at(V,A,T), not at(V,A,T+1), not a(A,1,T), not a(A,3,T), at(_,A,T+1).

% translate all actions into the ouput
output(1,move_left).output(2,move_forward).output(3,move_right).output(4,wait).
action(train(A),O',T) :- a(A,O,T), output(O,O').

#show action/3.
#show next/3.