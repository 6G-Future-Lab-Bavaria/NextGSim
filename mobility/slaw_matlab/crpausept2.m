function [list_cluster vplist]=...
    crpausept2(pausept, cluster, ratio_cluster, ratio_pausept, ocList, c_mode)
% function [list_cluster vplist]=...
%   crpausept2(pausept, cluster, ratio_cluster, ratio_pausept, ocList, c_mode)
%
% Description: Select clusters and corresponding visit points
%
% Seongik Hong, CSC, NCSU (2008/8/9)
% 
% Input arguments
%   pausept: set of pause points
%   B_range: clustering range
%   ocList: original cluster list
%   c_mode: 
%       1: give weight proportional to cluster size
%       2: 1 + change one of the selected clusters randomly
%       3: change one of the given cluster list and select vplist again
%
% Revision
% 1. give additional weight to bigger clusters
%    - weight is divided by # of clusters selected (in crand2.m, 2008/8/3)
%

%%
num_cluster = ceil(length(cluster(:,1))/ratio_cluster);
if c_mode == 3
    list_cluster = replacecluster(cluster, ocList);
else
    %list_cluster = crand(length(cluster(:,1)), num_cluster);
    list_cluster = crand2(cluster, num_cluster, c_mode); 
end

clist = [];
vplist = [];
for i=1:num_cluster
    idx = [];
    idx = find(cluster(list_cluster(i),:)==1);
    %
    clist(end+1:end+length(idx),:)=pausept(idx,:);
    l_idx = length(idx);
    % sihong, choose points in uniform manner
    aaa = l_idx/ratio_pausept;
    % add, 2008/8/17
    % when every cluster size is less than 1, 
    % newly selected points are zero &lt;- to prevent this condition
    if aaa < 1
        ttt = crand(l_idx,1);
        vplist(end+1:end+length(ttt),:)=pausept(idx(ttt),:);
    else
        % decimal
        aaa_dec = mod(aaa,1);
        % integer part
        aaa_int = aaa - aaa_dec;
        if rand < aaa_dec
            ttt = crand(l_idx,aaa_int+1);
            vplist(end+1:end+length(ttt),:)=pausept(idx(ttt),:);
        else
            if aaa_int > 0
                ttt = crand(l_idx,aaa_int);
                vplist(end+1:end+length(ttt),:)=pausept(idx(ttt),:);
            end
        end
    end
end 

%%
% sihong
% save('trace','vplist');
% pause;

% sihong, check point
% figure;
% plot(pausept(:,1),pausept(:,2),'bo');
% hold on; 
% plot(clist(:,1),clist(:,2),'rx');
% plot(vplist(:,1),vplist(:,2),'gs');
% legend('Total pause points', 'Selected cluster', 'Selected visit point');
% keyboard;			