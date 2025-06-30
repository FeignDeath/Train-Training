% get the chain of timesteps
at(V,A,T) :- dl((A,V),T).
next(A,T,T') :- at(V,A,T), at(V',A,T'), V!=V', T<T', V=VBetween: at(VBetween,A,T+1..T'-1).

% move to the previous position
a(A,O,T) :- next(A,T,T'), at(U,A,T), at(V,A,T'), wedge(U,V,N), turn(wedge(U,V,N),O), N>1.
a(A,2,T+1..T+N-2) :- next(A,T,T'), at(U,A,T), at(V,A,T'), wedge(U,V,N), N>1.
% wait at previous position
a(A,4,T+N-1..T'-2) :- next(A,T,T'), at(U,A,T), at(V,A,T'), wedge(U,V,N).
% last move to enter next position
a(A,O,T'-1) :- next(A,T,T'), at(U,A,T), at(V,A,T'), wedge(U,V,1), turn(wedge(U,V,1),O).
a(A,2,T'-1) :- next(A,T,T'), at(U,A,T), at(V,A,T'), wedge(U,V,N), N>1.

% implement the actions
% if a train traverses an edge to which takes 5 timesteps to traverse and hast 10 timesteps of time it should:
    % 0 turn correctly
    % 1-3 move forward
    % 4-8 wait
    % 9 move forward
% turn correctly
% a(A,O,T) :- next(A,T,T'), at(U,A,T), at(V,A,T'), turn(wedge(U,V,_),O), wedge(U,V,N), N>1.
% a(A,2,T) :- next(A,T,T'), at(U,A,T), at(V,A,T'), not turn(wedge(U,V,_),_), wedge(U,V,N), U != vertex(start), N>1.
% % move forward
% a(A,2,T+1..T+N-2) :- next(A,T,T'), at(U,A,T), at(V,A,T'), wedge(U,V,N), N>1.
% % wait for the leftover time
% a(A,4,T+N-1..T'-2) :- next(A,T,T'), at(U,A,T), at(V,A,T'), wedge(U,V,N), N>1.
% % last move
% a(A,2,T'-1) :- next(A,T,T'), at(U,A,T), at(V,A,T'), wedge(U,V,N), N>1.
% % what(A,2,T'-1) :- T'-1 = 34, next(A,T,T'), at(U,A,T), at(V,A,T'), wedge(U,V,N).
% % #show what/3.

% % if n is just 1, wait where you are and move last
% % wait
% a(A,4,T..T'-2) :- next(A,T,T'), at(U,A,T), at(V,A,T'), wedge(U,V,1).
% % turn correctly
% a(A,O,T'-1) :- next(A,T,T'), at(U,A,T), at(V,A,T'), wedge(U,V,1), turn(wedge(U,V,_),O).

% % add the at previously before(V,A,T,N)
% %     V next vertex
% %     A Agent
% %     T timestep where it is there
% %     N distance to v
% before(V,A,T+N-1..T'-2,-1) :- next(A,T,T'), at(U,A,T), at(V,A,T'), wedge(U,V,N).

% start handling
a(A,4,T..T'-2) :- at(vertex(start),A,T), next(A,T,T').
a(A,2,T'-1) :- at(vertex(start),A,T), next(A,T,T').

% translate all actions into the ouput
output(1,move_left).output(2,move_forward).output(3,move_right).output(4,wait).
action(train(A),O',T) :- a(A,O,T), output(O,O').

% safety constraint to see whether I messed something up
:- a(A,O,T), a(A,O',T), O<O'.
:- next(A,T1,T2), T=T1..T2-1, not a(A,_,T).

#show action/3.
% #show dl(B,C) : dl((0,vertex(B,_)),C).
% #show dl/2.
% #show error/2.
% % #show error/4.
% % #show error(A) : error(0,A).
% % % #show error(A,B,C) : error(1,A,B,C).
% #show dl(A,B) : dl((0,vertex(A,_)),B).
% #show dl(start,B) : dl((0,vertex(start)),B).
#show.
% #show before/4.
