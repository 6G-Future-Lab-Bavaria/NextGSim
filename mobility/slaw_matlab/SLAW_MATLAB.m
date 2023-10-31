function [v_trace] = SLAW_MATLAB(dist_alpha, num_user, x_max, y_max, n_wp, ...
    v_Hurst, Thours, B_range, beta, MIN_PAUSE, MAX_PAUSE)
%
% SLAW Trace Generator
% Written by Seongik Hong, NCSU, US (3/10/2009)
%	Waypoint Map Generator by Kyunghan Lee, KAIST, Korea
%
% Input arguments
%	dist_alpha: distance alpha (1 &lt; dist_alpha &lt; 6)
%	num_user: number of mobile users
%	size_max: a side of a right square simulation area
%	n_wp: number of waypoints
%	v_Hurst: Hurst parameter for self-similarity of waypoints 
%		(0.5 &lt; v_Hurst &lt; 1)
%	Thours: Total hours of trace generation (hours)
%	B_range: clustering range (meter)
%		If the waypoints are in B_range, they are considered as belonged to
%		the same cluster
%	beta: Levy exponent for pause time, 0 &lt; beta &lt;= 2
%	MIN_PAUSE: minimum pause time (second)
%	MAX_PAUSE: maximum pause time (second)
%
% Example:
%	trace = SLAW_MATLAB(3, 20, 2000, 2000, 0.75, 10, 50, 1, 30, 60*60);
%
% Based on the method of Kyunghan Lee (KAIST), Seongik Hong (NCSU),
%	Seong Joon Kim (NCSU), Injong Rhee (NCSU) and Song Chong (KAIST),
%	SLAW: A Mobility Model for Human Walks, The 28th IEEE
%	Conference on Computer Communications (INFOCOM), Rio de Janeiro,
%	Brazil, Apr. 2009.

%%
% simulation time (minute)
max_min = Thours*60;

%
ratio_cluster = 5;
ratio_pausept = 5;

%   1: give weight proportional to cluster size
%   2: 1 + replace one selected cluster in a random manner
c_mode = 2;

% Levy scale factor for pause time
sc_pause=1;

%sihong, sampling period (second)
t_gap = 60;

flight_mob = ['NS2_SLAW_' int2str(dist_alpha) '_' int2str(x_max) '.mob'];
fid_mob = fopen(flight_mob,'wt');


%%
% ------------------------------------------------------------------------
% Generate a waypoint map and make cluster information
% ------------------------------------------------------------------------

disp('... Waypoint map generation starts');

% generate a waypoint map
pausePt=[];
pausePt = makeSlawMap(x_max, y_max, n_wp, v_Hurst);
% save pausePt.mat pausePt;

% sihong, temp for test
% load pausePt.mat;

% mobility type definition
SLAW = 5;

% make clusters for the map
cluster = makecluster(pausePt, B_range);
% save cluster.mat cluster;

% sihong, temp for test
% load cluster.mat;

num_all_cluster=length(cluster(:,1));
% original cluster list for each users
o_clist=zeros(num_user,num_all_cluster);
num_all_pausePt=length(pausePt(:,1));
rPausePt=zeros(num_all_pausePt, 2, num_user);
lPausePt=zeros(num_user, 1);

disp('... Waypoint map generation done');


%%
% ------------------------------------------------------------------------
% mobility initialize START
% ------------------------------------------------------------------------
disp('... Initialization starts');

for i=1:num_user

	if mod(i,10)==0
		disp('.');
	end

	prev_start_time(i) = 0;
	pause_start_time(i) = 0;
	pause_end_time(i) = 0;

	mob_type(i) = SLAW;
	% sihong
	mob_subtype(i) = 1; % 0: non-destructive, 1:destructive
	% param = [alpha_ beta min_pt max_pt]
	%         1 &lt; dist_alpha &lt; 6, 0 &lt; beta &lt;= 2
	param=[dist_alpha beta MIN_PAUSE MAX_PAUSE];
end

for i=1:num_user
	if mod(i,10)==0
		disp('.');
	end

	mob_type(i) = SLAW;
	% 2x2 km^2
	% load('./ptKAIST/0928_st1_pt', 'pausept');
	mob_subtype(i) = 1; % 0: non-destructive, 1:destructive

	% param = [alpha_ beta min_pt max_pt]
	%         1 &lt; dist_alpha &lt; 6, 0 &lt; beta &lt;= 2
	param=[dist_alpha beta MIN_PAUSE MAX_PAUSE];

	%visit point list
	%vplist=[];
	%c_mode = 1
	[tmp_o_clist vplist]=crpausept2(pausePt, cluster, ratio_cluster, ratio_pausept,[], c_mode);
	o_clist(i,1:length(tmp_o_clist))=tmp_o_clist;

	lPausePt(i)=length(vplist(:,1));
	rPausePt(1:lPausePt(i),:,i)=vplist;
end

for i=1:num_user
	prev_xy(i,:) = rPausePt(ceil(rand*lPausePt(i)),:,i);
	next_xy(i,:) = rPausePt(ceil(rand*lPausePt(i)),:,i);
end

tmp = rand(num_user,1);
crnt_xy = prev_xy +  [tmp tmp].* (next_xy-prev_xy);
visitedPt = zeros(num_user, num_all_pausePt);

disp('... Initialization done');

%%
% ------------------------------------------------------------------------
% Trace generation
% ------------------------------------------------------------------------

disp('... Trace generation starts');

t_start = 1;
idx_ = 1;
v_trace=[];

for t=t_start:t_gap:max_min*60
	for i=1:num_user %
		[prev_start_time(i), pause_start_time(i), pause_end_time(i), ...
			prev_xy(i,:), next_xy(i,:), crnt_xy(i,:), visitedPt(i,:), ...
			isChangedPoints, vPoints, ...
			flight_t, pause_t, rttimes_t] ...
			= findpositionbslw(t, prev_xy(i,:), next_xy(i,:), ...
			pausePt, cluster, ratio_cluster, ratio_pausept, o_clist(i,:),...
			prev_start_time(i), pause_start_time(i), pause_end_time(i), sc_pause, ...
			mob_type(i), mob_subtype(i), param, rPausePt(:,:,i), visitedPt(i,:), lPausePt(i));

		if isChangedPoints == 1
			lPausePt(i)=length(vPoints(:,1));
			rPausePt(1:lPausePt(i),:,i)=vPoints;
			rPausePt(lPausePt(i)+1:end,:,i)=0;
		end
		
		v_trace(i,idx_, 1) = crnt_xy(i,1);
		v_trace(i,idx_, 2) = crnt_xy(i,2);
		v_trace(i,idx_, 3) = t;
	end

	idx_ = idx_ + 1;
end

fclose(fid_mob);

disp('... Trace generation done');