function r_cluster = makecluster(pausept, B_range)
% function r_cluster = makecluster(pausept, B_range)
% Seongik Hong, 3/1/2008
% Input argument :
%   pausept(:,1) : x location, pausept(:,2) : y location
%   B_range : clustering range

disp('... makecluster called');

% t_clock = clock;  

newmember=[1];
nonmember=zeros(1,length(pausept(:,1)));
r_cluster=[];
num_crt_cluster=0;
tmp_cluster=zeros(1,length(pausept(:,1)));
tmp_cluster(1)=1;

for i=2:length(pausept(:,1))
    nonmember(i)=i;
end

while length(find(nonmember~=0))
    while length(newmember)~=0
        idx=find(nonmember~=0);
        for i=1:length(idx)
            if dist(pausept(newmember(1),:)', pausept(idx(i),:)') <= B_range
                newmember=[newmember idx(i)];
                nonmember(idx(i))=0;
                tmp_cluster(idx(i))=1;
            end
        end
        newmember=newmember(2:end);
    end
    num_crt_cluster=num_crt_cluster+1;
    r_cluster(num_crt_cluster,:)=tmp_cluster;
    
    idx=find(nonmember~=0);
    if idx
        newmember=idx(1);
        tmp_cluster=zeros(1,length(pausept(:,1)));
        tmp_cluster(idx(1))=1;
    else
        break;
    end
end

disp('    Number of clusters: ');
disp(length(r_cluster(:,1)));

% ttt=etime(clock, t_clock);
% str_ttt = ['Elapsed time : ' num2str(ttt)];
% display(str_ttt);

disp('... makecluster done');			