close all
t=200
figure()
subplot(2,2,1)
load('Hetereogeneity/C10seed1.mat')
Scenario_draw(200)
hold on
plot(trace(:,t,1)-250,trace(:,t,2)-250,'*')
subplot(2,2,2)
hold on
load('Hetereogeneity/B10seed1.mat')
Scenario_draw(200)
plot(trace(:,t,1)-250,trace(:,t,2)-250,'*')

subplot(2,2,3)
hold on
load('Hetereogeneity/C10seed1.mat')
Scenario_draw(200)
plot(trace(:,t,1)-250,trace(:,t,2)-250,'*')
subplot(2,2,4)
hold on
load('Hetereogeneity/U50seed1.mat')
Scenario_draw(200)
plot(trace(:,t,1)-250,trace(:,t,2)-250,'*')
% subplot(2,2,4)
% hold on
% load('Hetereogeneity/H5000seed1.mat')
% Scenario_draw(200)
% plot(trace(:,t,1)-250,trace(:,t,2)-250,'*')