function clist = crand2(cluster, k, c_mode)
% function clist = crand2(cluster, k, c_mode)
% Description: select cluster list
% Seongik Hong, CSC, NCSU (2008/8/3)
% 
% Input arguments
%   c_mode: 
%       1: give weight proportional to cluster size (default)
%       2: replace one of the selected clusters
%
% Revision history
% 1. choose k from cluster list giving more weight to bigger one
% 2. Add c_mode (2008/8/5)
%    2: replace one of the clusters randomly

%%
clist=[];
% number of clusters
l_cluster=length(cluster(:,1));

% there should be one random selection
if k > l_cluster
    disp('... k should not be larger than the number of clusters');
    return;
end

% check every cluster size
for i=1:l_cluster
    l_size(i)=length(find(cluster(i,:)==1));
end


%% 
n_a=[];
for i=1:l_cluster
    for j=1:l_size(i)
        n_a=[n_a i];
    end
end
n=length(n_a);

% 
while 1
    isAlreadyIn=0;
    tmp=n_a(ceil(rand*n));
    for i=1:length(clist)
        if clist(i)==tmp
            isAlreadyIn=1;
            break;
        end
    end
    if isAlreadyIn==0
        clist=[clist tmp];
    end
    if length(clist)==k        
        break;
    end
end

%%
% Added by revision 2.
% replace one of the selected clusters randomly
if c_mode == 2
    clist = replacecluster(cluster, clist);
end

% keyboard; 			