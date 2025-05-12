%% generating ordered cyclefree paths

% move to enter the map
move(A,vertex(start),U) :- first_vertex(A,U).
% move to leave the map
1 {move(A,V,vertex(end)): last_vertex(A,V)} 1 :- agent(A).

% choice rule for moves, only one is needed
% every vertex may be left via up to une move
{move(A,U,V): edge(U,V)} 1 :- agent(A), edge(U,_).
% every move may have a follow up move
% {move(A,U,V): edge(U,V)} 1 :- move(A,_,U).

% all moves except the start one, must have one before them
:- move(A,U,_), not move(A,_,U), U!=vertex(start).
% all moves except the last one, must have one after them
:- move(A,_,V), not move(A,V,_), V!=vertex(end).

% every move has no more than 1 leading up to it
:- move(A,V,_), 2 {move(A,_,V)}.

%% ensuring goals are reached and conflicts enforced

% choose who gets priority
1 {resolve((A,U),(B,V)); resolve((B,V),(A,U))} 1 :- move(A,_,U), move(B,_,V), shared_resource(U,V), A<B.

#edge((A,U),(A,V)) : move(A,U,V).
#edge((A,V),(B,W)) : resolve((A,U),(B,W)), move(A,U,V).

% the goal must be reached in time
goal(A) :- state(A,vertex(end),_), agent(A).
:- agent(A), not goal(A).

%% generating a path from the moveset before

% start vertex at earliest possible timestep
state(A,vertex(start),T) :- T = #max{T': start(A,_,T',_); 1}, agent(A).

% an agent may wait or continue along his path
{state(A,U,T)} :- state(A,U,T-1), move(A,U,V), T<=L, end(A,_,L).
state(A,V,T) :- state(A,U,T-1), move(A,U,V), not state(A,U,T), T<=L, end(A,_,L).

% agent must conform the the ordering
:- resolve((A,U),(B,W)), move(A,U,V), state(A,V,T1), state(B,W,T2), T1>T2.