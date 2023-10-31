function clist=replacecluster(cluster, clist)
% function clist=replacecluster(cluster, clist)
% Description: replace one of selected clusters randomly
%  and return new cluster list
%
% Seongik Hong, CSC, NCSU (2008/8/7)
% 
% Input arguments
%   cluster: cluster info matrix
%   clist: original cluster list
%

%%
% number of clusters
l_cluster=length(cluster(:,1));
% select the index of the cluster that will be deleted
d_i_cluster = ceil(rand*length(clist));

while 1
    isAlreadyIn=0;
    new_cluster = ceil(rand*l_cluster);
    for i=1:length(clist)
        if clist(i)==new_cluster
            isAlreadyIn=1;
            break;
        end
    end
    if isAlreadyIn == 0
        clist(d_i_cluster) = new_cluster;
        break;
    end
end			