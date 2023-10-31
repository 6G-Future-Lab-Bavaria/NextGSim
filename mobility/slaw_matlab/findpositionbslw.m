function [prev_start_time, pause_start_time, pause_end_time, ...
          prev_xy, next_xy, crnt_xy, isVisited, ...
          isChangedPoints, vPoints, ...
          flights, pauses, rttimes] = findpositionbslw( ...
          t, prev_xy, next_xy, ...
          pausePt, cluster, ratio_cluster, ratio_pausept, o_clist, ...
          prev_start_time, pause_start_time, pause_end_time, sc_pause, ...
          mob_type, mob_subtype, param, visitLocations, isVisited, lVisitLocations)
%
% Description: find node position by SLAW model at time t
%
% Written by Seongik Hong, NCSU (8/7/2008)
%
% param = [alpha_ beta min_pt max_pt]
% 1 &lt; alpha_ &lt; 6, 1 &lt; beta &lt;= 2
%

%%
SLAW = 5;

alpha_=param(1); beta=param(2); min_pt=param(3); max_pt=param(4);
if mob_type ~= SLAW
    error('Error: SLAW Model type should be called.')
end

% visit point set
ocList = o_clist(find(o_clist > 0));
l_ocList = length(ocList);
vPoints=visitLocations(1:lVisitLocations,:);
isVisited(1,lVisitLocations+1:end)=1;
isChangedPoints = 0;
% velocity
velocity=1;

%%
flights=[]; 
pauses=[];
%round trip time
rttimes=0;

while (t > pause_end_time)
    prev_start_time = pause_end_time;
    prev_xy = next_xy;
    
    p_time = powerlaw_rnd(beta, min_pt, max_pt, 1, sc_pause, 1);
    
    % calculate distance to every pause point from prev_xy
    dist_ = sqrt((vPoints(:,1)-prev_xy(1)).^2 + (vPoints(:,2)-prev_xy(2)).^2);
    % index for other points except the previous point
    idx = find(dist_ > 0);
    % set prev_xy point as 'visited'
    % 'visited' = 1
    isVisited(find(dist_==0))=1;
    if mob_subtype == 1
        % destructive case
        idx = find(isVisited==0);
        % all visit points are visited
        if isempty(idx)
            % Set round trip time
            rttimes = t;
            %
            [new_clist, new_vPoints] = ...
                crpausept2(pausePt, cluster, ratio_cluster, ratio_pausept, ocList, 3);
            vPoints=[];
            vPoints=new_vPoints;
            if isempty(vPoints)
                disp('Error: No visit point selected');
            end
            isVisited(1:length(new_vPoints))=0;
                
            %sihong, plot all the visit points to plot a sample trace
            %TEST
            %figure;
            %plot(pausePt(:,1),pausePt(:,2),'g.');
            %axis([0 8 0 8])
            %hold on;

            dist_ = sqrt((vPoints(:,1)-prev_xy(1)).^2 + (vPoints(:,2)-prev_xy(2)).^2);
            idx = find(dist_ > 0);
                
            isChangedPoints = 1;
        end
    end
    dist_= dist_(idx);
	if isempty(dist_)
		disp('Error: length(dist_) == 0')
	end
    weight_ = cumsum(1./(dist_).^alpha_); 
    weight_ = weight_/weight_(end);
    next_xy = vPoints(idx(min(find(weight_ > rand(1,1)))),:);

    flights = [flights norm(next_xy - prev_xy)];
    pauses = [pauses p_time];
    
    pause_start_time = prev_start_time + norm(next_xy - prev_xy) / velocity;
    pause_end_time = pause_start_time + p_time;
end

%%

if t >= prev_start_time && t < pause_start_time
    [crnt_xy, rem_length] = lin_interpolate(prev_xy, next_xy, prev_start_time, pause_start_time, t);
    %direction = phase( (next_xy(1) - prev_xy(1)) + (next_xy(2) - prev_xy(2))*i);
    %v = norm(next_xy - prev_xy)/(pause_start_time - prev_start_time);
%8/7
%elseif t &gt;= pause_start_time &amp;&amp; t &lt; pause_end_time
elseif t >= pause_start_time && t <= pause_end_time
    crnt_xy = next_xy; 
    rem_length = 0;
    %direction = phase( (next_xy(1) - prev_xy(1)) + (next_xy(2) - prev_xy(2))*i);
    %v = 0;    
end

%%
%------------------------------------------------------------
function [crnt_xy, rem_length] = lin_interpolate(prev_xy, next_xy, prev_start_time, pause_start_time, t)
%------------------------------------------------------------
t_gap = (pause_start_time - prev_start_time);

if t_gap == 0
    crnt_xy = prev_xy;
    rem_length = 0;
    return;
end
t_deg = (t - prev_start_time);
crnt_xy = prev_xy + (next_xy - prev_xy) * t_deg / t_gap;
rem_length = norm(next_xy - crnt_xy);
%------------------------------------------------------------			