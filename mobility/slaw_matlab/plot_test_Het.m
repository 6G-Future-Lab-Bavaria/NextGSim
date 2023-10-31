close all

t=100
% counter=0;
% for i=[0.1:0.1:0.7]
%     i
%     counter=i*10;
%     try
%     subplot(3,3,counter)
%     filename = strcat('./Hetereogeneity/i',num2str(counter),'seed',num2str(seed));
%     load(filename)
%     hold on
%     plot(trace(:,t,1),trace(:,t,2),'r*')
%     catch
%         disp('a')
%     end
% end
seed=1
subplot(3,2,1)
filename = strcat('./Hetereogeneity/H2/H2_seed',num2str(seed));
load(filename);plot(trace(:,t,1),trace(:,t,2),'r*')
seed=1
subplot(3,2,2)
filename = strcat('./Hetereogeneity/H3/H3_seed',num2str(seed));
load(filename);plot(trace(:,t,1),trace(:,t,2),'r*')
seed=1
subplot(3,2,3)
filename = strcat('./Hetereogeneity/H1/H1_seed',num2str(seed));
load(filename);plot(trace(:,t,1),trace(:,t,2),'r*')
seed=5
subplot(3,2,4)
filename = strcat('./Hetereogeneity/H5/H52_seed',num2str(seed));
load(filename);plot(trace(:,t,1),trace(:,t,2),'r*')
seed=1
subplot(3,2,5)
filename = strcat('./Hetereogeneity/H6/H6_seed',num2str(seed));
load(filename);plot(trace(:,t,1),trace(:,t,2),'r*')
seed=1
subplot(3,2,6)
filename = strcat('./Hetereogeneity/H2/H2_seed',num2str(seed));
load(filename);plot(trace(:,t,1),trace(:,t,2),'r*')


