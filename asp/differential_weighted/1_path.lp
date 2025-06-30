%% generating ordered cyclefree paths

% move to enter the map
move(A,vertex(start),U) :- first_vertex(A,U).
% move to leave the map
1 {move(A,V,vertex(end)): last_vertex(A,V)} 1 :- agent(A).

% choice rule for moves, only one is needed
% every vertex may be left via up to une move
{move(A,U,V): wedge(U,V,_)} 1 :- agent(A), edge(U,_).
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

% previous moves need previous timesteps
&diff{(A,U)+N} <= (A,V) :- move(A,U,V), wedge(U,V,N).
% trains going first need to be gone before the next enters the field
%   this is to strict and also forbids follow up conflicts, which in turn dissallows swap conflicts
&diff{(A,W)+N} <= (B,V) :- resolve((A,U),(B,V)), move(A,U,W), wedge(U,W,N).

% the unspawned train exists from zero onwards
&diff{(A,vertex(start))} = 0 :- agent(A).
% no train can spawn earlier than allowed
&diff{(A,U)} > T :- start(A,_,T,_), move(A,vertex(start),U).
&diff{(A,U)} > 1 :- start(A,_,T,_), move(A,vertex(start),U).
% goal needs to be reached in time
&diff{(A,U)-0} <= T :- end(A,_,T), move(A,U,vertex(end)).

% #show turn/2.
% #show wedge/3.