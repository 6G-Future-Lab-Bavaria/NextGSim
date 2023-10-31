clc,close all,clear all

minutes=1/2; simulationTime=120;warmup=0; %seconds

bsN=7;sectors=3;interdistance=200;
seed=1;
users=7*3*5;
operators=3;
s_o=(1/operators)*ones(1,operators);belonging= get_belonging(s_o,users,operators);
s_o=belonging/users;
% Network settings
[ NetSettings ] = Network_Settings(saturation,bsN,interdistance,users,simulationTime,warmup);
NetSettings.D=230;
% Operator settings
[ OpSettings ] = Operators_Settings(operators,s_o,belonging,NetSettings);


%% Users settings
dist_alpha=1;
beta=1;
MIN_PAUSE=1;
MAX_PAUSE=5;

size_max=500;
Thours=0.002;

n_wp=100
v_Hurst=0.99;
B_range=30;
%% Generate user movements
trace=SLAW_MATLAB(dist_alpha, users, size_max, n_wp, v_Hurst,Thours, B_range, beta, MIN_PAUSE, MAX_PAUSE);
 %% Scenario
[ bs_positions ] = Scenario_Generation(NetSettings);

%% Link estimation
[ c_ijt ] = Link_Estimation(NetSettings,trace,bs_positions,4);
t=120   
[~, assoc]=max( c_ijt(:,:,t)' );
figure()
hist(assoc,21)
pause()
filename = strcat('./Hetereogeneity/U',num2str(n_wp),'seed',num2str(seed));
save(filename)
