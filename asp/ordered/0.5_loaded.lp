%% This serves to:
%% 1. Save atoms that should survive a malfunction, and will be used in the next scheduling.
%% 2. Load said atoms, given the previous state.

%% 1. Mandatory, respecting the current problem context.
save(action(A,O,T)) :- action(A,O,T). % General rule
save(dl(X,T)):- dl(X,T). %Custom for our solution
%% 1. Efficiency choices, you probably want to customize these to your solution
save(trackparts(Pos,D1,D2)):- trackparts(Pos,D1,D2). %available cell directions
save(vertex(Pos,Dir)):- vertex(Pos,Dir).%trackpars + cell
save(edge(V1,V2)):- edge(V1,V2). % connectivity between vertex(trackpart+cell)
save(turn(Edg,Ver,Dir)):- turn(Edg,Ver,Dir). %does the edge imply a turn
save(shared_resources(VE1,VE2)):- shared_resources(VE1,VE2). %detecting vector-edge share conflicts




%% 2. Mandatory 
action(A,O,T):- load(action(A,O,T)), malfunction(_,_,TLast), TLast> T.
dl(X,T):- load(dl(X,T)), malfunction(_,_,TLast), TLast> T.
%% 2. Efficiency choices 
trackparts(Pos,D1,D2):- load(trackparts(Pos,D1,D2)). %available cell directions
vertex(Pos,Dir):- load(vertex(Pos,Dir)).%trackpars + cell
edge(V1,V2):- load(edge(V1,V2)). % connectivity between vertex(trackpart+cell)
turn(Edg,Ver,Dir):- load(turn(Edg,Ver,Dir)). %does the edge imply a turn
shared_resources(VE1,VE2):- load(shared_resources(VE1,VE2)). %detecting vector-edge share conflicts



