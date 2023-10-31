function [bs] = Scenario_draw(intersiteD)

x_hexagon=[-1 -0.5 0.5 1 0.5 -0.5 -1];
y_hexagon=[0 -sqrt(3)/2 -sqrt(3)/2 0 sqrt(3)/2 sqrt(3)/2 0];
multiple=intersiteD/(2*cosd(30));
s1=[1,0];
s2=[-0.5,sqrt(3)/2];
s3=[-0.5,-sqrt(3)/2];

figure(1)
hold on
%% mesh grid
%%
plot(multiple*(x_hexagon+3*0),multiple*(y_hexagon+sqrt(3)*0),'b-')
plot(multiple*(x_hexagon+1.5+3*0),multiple*(y_hexagon+sqrt(3)/2+sqrt(3)*0),'b-')
plot(multiple*(x_hexagon-1.5+3*0),multiple*(y_hexagon-sqrt(3)/2+sqrt(3)*0),'b-')
plot(multiple*(x_hexagon+1.5+3*0),multiple*(y_hexagon+sqrt(3)/2+sqrt(3)*1),'b-')
plot(multiple*(x_hexagon-1.5+3*0),multiple*(y_hexagon-sqrt(3)/2+sqrt(3)*1),'b-')
plot(multiple*(x_hexagon+1.5+3*0),multiple*(y_hexagon+sqrt(3)/2+sqrt(3)*-1),'b-')
plot(multiple*(x_hexagon-1.5+3*0),multiple*(y_hexagon-sqrt(3)/2+sqrt(3)*-1),'b-')
plot(multiple*(x_hexagon+1.5+3*0),multiple*(y_hexagon+sqrt(3)/2+sqrt(3)*-2),'b-')
plot(multiple*(x_hexagon+3*0),multiple*(y_hexagon+sqrt(3)*1),'b-')
plot(multiple*(x_hexagon+3*0),multiple*(y_hexagon+sqrt(3)*2),'b-')
plot(multiple*(x_hexagon+3*0),multiple*(y_hexagon+sqrt(3)*-1),'b-')
plot(multiple*(x_hexagon+3*1),multiple*(y_hexagon+sqrt(3)*0),'b-')
plot(multiple*(x_hexagon+3*1),multiple*(y_hexagon+sqrt(3)*-1),'b-')
plot(multiple*(x_hexagon+3*1),multiple*(y_hexagon+sqrt(3)*1),'b-')
plot(multiple*(x_hexagon+3*-1),multiple*(y_hexagon+sqrt(3)*0),'b-')
plot(multiple*(x_hexagon+3*-1),multiple*(y_hexagon+sqrt(3)*-1),'b-')
plot(multiple*(x_hexagon+3*-1),multiple*(y_hexagon+sqrt(3)*1),'b-')
plot(multiple*(x_hexagon-1.5+3*0),multiple*(y_hexagon+sqrt(3)/2+sqrt(3)*1),'b-')
plot(multiple*(x_hexagon+3*0),multiple*(y_hexagon+sqrt(3)*-2),'b-')

plot([multiple*(1.5+3*0) multiple*(s1(1)+1.5+3*0)],[multiple*(sqrt(3)/2+sqrt(3)*-2) multiple*(s1(2)+sqrt(3)/2+sqrt(3)*-2)],'k:')
plot([multiple*(1.5+3*0) multiple*(s2(1)+1.5+3*0)],[multiple*(sqrt(3)/2+sqrt(3)*-2) multiple*(s2(2)+sqrt(3)/2+sqrt(3)*-2)],'k:')
plot([multiple*(1.5+3*0) multiple*(s3(1)+1.5+3*0)],[multiple*(sqrt(3)/2+sqrt(3)*-2) multiple*(s3(2)+sqrt(3)/2+sqrt(3)*-2)],'k:')
plot([multiple*(1.5+3*0) multiple*(s1(1)+1.5+3*0)],[multiple*(sqrt(3)/2+sqrt(3)*-1) multiple*(s1(2)+sqrt(3)/2+sqrt(3)*-1)],'k:')
plot([multiple*(1.5+3*0) multiple*(s2(1)+1.5+3*0)],[multiple*(sqrt(3)/2+sqrt(3)*-1) multiple*(s2(2)+sqrt(3)/2+sqrt(3)*-1)],'k:')
plot([multiple*(1.5+3*0) multiple*(s3(1)+1.5+3*0)],[multiple*(sqrt(3)/2+sqrt(3)*-1) multiple*(s3(2)+sqrt(3)/2+sqrt(3)*-1)],'k:')
plot([multiple*(1.5+3*0) multiple*(s1(1)+1.5+3*0)],[multiple*(sqrt(3)/2+sqrt(3)*0) multiple*(s1(2)+sqrt(3)/2+sqrt(3)*0)],'k:')
plot([multiple*(1.5+3*0) multiple*(s2(1)+1.5+3*0)],[multiple*(sqrt(3)/2+sqrt(3)*0) multiple*(s2(2)+sqrt(3)/2+sqrt(3)*0)],'k:')
plot([multiple*(1.5+3*0) multiple*(s3(1)+1.5+3*0)],[multiple*(sqrt(3)/2+sqrt(3)*0) multiple*(s3(2)+sqrt(3)/2+sqrt(3)*0)],'k:')
plot([multiple*(1.5+3*0) multiple*(s1(1)+1.5+3*0)],[multiple*(sqrt(3)/2+sqrt(3)*1) multiple*(s1(2)+sqrt(3)/2+sqrt(3)*1)],'k:')
plot([multiple*(1.5+3*0) multiple*(s2(1)+1.5+3*0)],[multiple*(sqrt(3)/2+sqrt(3)*1) multiple*(s2(2)+sqrt(3)/2+sqrt(3)*1)],'k:')
plot([multiple*(1.5+3*0) multiple*(s3(1)+1.5+3*0)],[multiple*(sqrt(3)/2+sqrt(3)*1) multiple*(s3(2)+sqrt(3)/2+sqrt(3)*1)],'k:')
plot([multiple*(-1.5+3*0) multiple*(s1(1)-1.5+3*0)],[multiple*(sqrt(3)/2+sqrt(3)*-2) multiple*(s1(2)+sqrt(3)/2+sqrt(3)*-2)],'k:')
plot([multiple*(-1.5+3*0) multiple*(s2(1)-1.5+3*0)],[multiple*(sqrt(3)/2+sqrt(3)*-2) multiple*(s2(2)+sqrt(3)/2+sqrt(3)*-2)],'k:')
plot([multiple*(-1.5+3*0) multiple*(s3(1)-1.5+3*0)],[multiple*(sqrt(3)/2+sqrt(3)*-2) multiple*(s3(2)+sqrt(3)/2+sqrt(3)*-2)],'k:')
plot([multiple*(-1.5+3*0) multiple*(s1(1)-1.5+3*0)],[multiple*(sqrt(3)/2+sqrt(3)*-1) multiple*(s1(2)+sqrt(3)/2+sqrt(3)*-1)],'k:')
plot([multiple*(-1.5+3*0) multiple*(s2(1)-1.5+3*0)],[multiple*(sqrt(3)/2+sqrt(3)*-1) multiple*(s2(2)+sqrt(3)/2+sqrt(3)*-1)],'k:')
plot([multiple*(-1.5+3*0) multiple*(s3(1)-1.5+3*0)],[multiple*(sqrt(3)/2+sqrt(3)*-1) multiple*(s3(2)+sqrt(3)/2+sqrt(3)*-1)],'k:')
plot([multiple*(-1.5+3*0) multiple*(s1(1)-1.5+3*0)],[multiple*(sqrt(3)/2+sqrt(3)*0) multiple*(s1(2)+sqrt(3)/2+sqrt(3)*0)],'k:')
plot([multiple*(-1.5+3*0) multiple*(s2(1)-1.5+3*0)],[multiple*(sqrt(3)/2+sqrt(3)*0) multiple*(s2(2)+sqrt(3)/2+sqrt(3)*0)],'k:')
plot([multiple*(-1.5+3*0) multiple*(s3(1)-1.5+3*0)],[multiple*(sqrt(3)/2+sqrt(3)*0) multiple*(s3(2)+sqrt(3)/2+sqrt(3)*0)],'k:')
plot([multiple*(-1.5+3*0) multiple*(s1(1)-1.5+3*0)],[multiple*(sqrt(3)/2+sqrt(3)*1) multiple*(s1(2)+sqrt(3)/2+sqrt(3)*1)],'k:')
plot([multiple*(-1.5+3*0) multiple*(s2(1)-1.5+3*0)],[multiple*(sqrt(3)/2+sqrt(3)*1) multiple*(s2(2)+sqrt(3)/2+sqrt(3)*1)],'k:')
plot([multiple*(-1.5+3*0) multiple*(s3(1)-1.5+3*0)],[multiple*(sqrt(3)/2+sqrt(3)*1) multiple*(s3(2)+sqrt(3)/2+sqrt(3)*1)],'k:')
plot([multiple*(3*0) multiple*(s1(1)+3*0)],[multiple*(sqrt(3)*0) multiple*(s1(2)+sqrt(3)*0)],'k:')
plot([multiple*(3*0) multiple*(s2(1)+3*0)],[multiple*(sqrt(3)*0) multiple*(s2(2)+sqrt(3)*0)],'k:')
plot([multiple*(3*0) multiple*(s3(1)+3*0)],[multiple*(sqrt(3)*0) multiple*(s3(2)+sqrt(3)*0)],'k:')
plot([multiple*(3*-1) multiple*(s1(1)+3*-1)],[multiple*(sqrt(3)*0) multiple*(s1(2)+sqrt(3)*0)],'k:')
plot([multiple*(3*-1) multiple*(s2(1)+3*-1)],[multiple*(sqrt(3)*0) multiple*(s2(2)+sqrt(3)*0)],'k:')
plot([multiple*(3*-1) multiple*(s3(1)+3*-1)],[multiple*(sqrt(3)*0) multiple*(s3(2)+sqrt(3)*0)],'k:')
plot([multiple*(3*1) multiple*(s1(1)+3*1)],[multiple*(sqrt(3)*0) multiple*(s1(2)+sqrt(3)*0)],'k:')
plot([multiple*(3*1) multiple*(s2(1)+3*1)],[multiple*(sqrt(3)*0) multiple*(s2(2)+sqrt(3)*0)],'k:')
plot([multiple*(3*1) multiple*(s3(1)+3*1)],[multiple*(sqrt(3)*0) multiple*(s3(2)+sqrt(3)*0)],'k:')
plot([multiple*(3*1) multiple*(s1(1)+3*1)],[multiple*(sqrt(3)*1) multiple*(s1(2)+sqrt(3)*1)],'k:')
plot([multiple*(3*1) multiple*(s2(1)+3*1)],[multiple*(sqrt(3)*1) multiple*(s2(2)+sqrt(3)*1)],'k:')
plot([multiple*(3*1) multiple*(s3(1)+3*1)],[multiple*(sqrt(3)*1) multiple*(s3(2)+sqrt(3)*1)],'k:')
plot([multiple*(3*-1) multiple*(s1(1)+3*-1)],[multiple*(sqrt(3)*1) multiple*(s1(2)+sqrt(3)*1)],'k:')
plot([multiple*(3*-1) multiple*(s2(1)+3*-1)],[multiple*(sqrt(3)*1) multiple*(s2(2)+sqrt(3)*1)],'k:')
plot([multiple*(3*-1) multiple*(s3(1)+3*-1)],[multiple*(sqrt(3)*1) multiple*(s3(2)+sqrt(3)*1)],'k:')
plot([multiple*(3*-1) multiple*(s1(1)+3*-1)],[multiple*(sqrt(3)*-1) multiple*(s1(2)+sqrt(3)*-1)],'k:')
plot([multiple*(3*-1) multiple*(s2(1)+3*-1)],[multiple*(sqrt(3)*-1) multiple*(s2(2)+sqrt(3)*-1)],'k:')
plot([multiple*(3*-1) multiple*(s3(1)+3*-1)],[multiple*(sqrt(3)*-1) multiple*(s3(2)+sqrt(3)*-1)],'k:')
plot([multiple*(3*1) multiple*(s1(1)+3*1)],[multiple*(sqrt(3)*-1) multiple*(s1(2)+sqrt(3)*-1)],'k:')
plot([multiple*(3*1) multiple*(s2(1)+3*1)],[multiple*(sqrt(3)*-1) multiple*(s2(2)+sqrt(3)*-1)],'k:')
plot([multiple*(3*1) multiple*(s3(1)+3*1)],[multiple*(sqrt(3)*-1) multiple*(s3(2)+sqrt(3)*-1)],'k:')
plot([multiple*(3*0) multiple*(s1(1)+3*0)],[multiple*(sqrt(3)*1) multiple*(s1(2)+sqrt(3)*1)],'k:')
plot([multiple*(3*0) multiple*(s2(1)+3*0)],[multiple*(sqrt(3)*1) multiple*(s2(2)+sqrt(3)*1)],'k:')
plot([multiple*(3*0) multiple*(s3(1)+3*0)],[multiple*(sqrt(3)*1) multiple*(s3(2)+sqrt(3)*1)],'k:')
plot([multiple*(3*0) multiple*(s1(1)+3*0)],[multiple*(sqrt(3)*2) multiple*(s1(2)+sqrt(3)*2)],'k:')
plot([multiple*(3*0) multiple*(s2(1)+3*0)],[multiple*(sqrt(3)*2) multiple*(s2(2)+sqrt(3)*2)],'k:')
plot([multiple*(3*0) multiple*(s3(1)+3*0)],[multiple*(sqrt(3)*2) multiple*(s3(2)+sqrt(3)*2)],'k:')
plot([multiple*(3*0) multiple*(s1(1)+3*0)],[multiple*(sqrt(3)*-1) multiple*(s1(2)+sqrt(3)*-1)],'k:')
plot([multiple*(3*0) multiple*(s2(1)+3*0)],[multiple*(sqrt(3)*-1) multiple*(s2(2)+sqrt(3)*-1)],'k:')
plot([multiple*(3*0) multiple*(s3(1)+3*0)],[multiple*(sqrt(3)*-1) multiple*(s3(2)+sqrt(3)*-1)],'k:')
plot([multiple*(3*0) multiple*(s1(1)+3*0)],[multiple*(sqrt(3)*-2) multiple*(s1(2)+sqrt(3)*-2)],'k:')
plot([multiple*(3*0) multiple*(s2(1)+3*0)],[multiple*(sqrt(3)*-2) multiple*(s2(2)+sqrt(3)*-2)],'k:')
plot([multiple*(3*0) multiple*(s3(1)+3*0)],[multiple*(sqrt(3)*-2) multiple*(s3(2)+sqrt(3)*-2)],'k:')
%% Out grip
% plot(multiple*(x_hexagon+3*0),multiple*(y_hexagon+sqrt(3)*-3),':k')
% plot(multiple*(x_hexagon-1.5+3*0),multiple*(y_hexagon+sqrt(3)/2+sqrt(3)*2),':k')
% plot(multiple*(x_hexagon+3*-1),multiple*(y_hexagon+sqrt(3)*2),':k')
% plot(multiple*(x_hexagon+3*-1),multiple*(y_hexagon+sqrt(3)*-2),':k')
% plot(multiple*(x_hexagon+3*1),multiple*(y_hexagon+sqrt(3)*2),':k')
% plot(multiple*(x_hexagon+3*1),multiple*(y_hexagon+sqrt(3)*-2),':k')
% plot(multiple*(x_hexagon+3*0),multiple*(y_hexagon+sqrt(3)*3),':k')
% plot(multiple*(x_hexagon+1.5+3*0),multiple*(y_hexagon+sqrt(3)/2+sqrt(3)*2),':k')
% plot(multiple*(x_hexagon+1.5+3*0),multiple*(y_hexagon+sqrt(3)/2+sqrt(3)*-3),':k')
% plot(multiple*(x_hexagon-1.5+3*0),multiple*(y_hexagon-sqrt(3)/2+sqrt(3)*-2),':k')
% plot(multiple*(x_hexagon+1.5+3*1),multiple*(y_hexagon+sqrt(3)/2+sqrt(3)*-1),':k')
% plot(multiple*(x_hexagon-1.5+3*2),multiple*(y_hexagon-sqrt(3)/2+sqrt(3)*1),':k')
% plot(multiple*(x_hexagon+1.5+3*1),multiple*(y_hexagon+sqrt(3)/2+sqrt(3)*-2),':k')
% plot(multiple*(x_hexagon+1.5+3*-2),multiple*(y_hexagon+sqrt(3)/2+sqrt(3)*-2),':k')
% plot(multiple*(x_hexagon+1.5+3*-2),multiple*(y_hexagon+sqrt(3)/2+sqrt(3)*-1),':k')
% plot(multiple*(x_hexagon+1.5+3*-2),multiple*(y_hexagon+sqrt(3)/2+sqrt(3)*0),':k')
% plot(multiple*(x_hexagon+1.5+3*-2),multiple*(y_hexagon+sqrt(3)/2+sqrt(3)*1),':k')
% plot(multiple*(x_hexagon+1.5+3*1),multiple*(y_hexagon+sqrt(3)/2+sqrt(3)*1),':k')

% % plot(multiple*(x_hexagon+3*0),multiple*(y_hexagon+sqrt(3)*-4),':k')
% % plot(multiple*(x_hexagon+3*0),multiple*(y_hexagon+sqrt(3)*4),':k')
% % plot(multiple*(x_hexagon+3*-1),multiple*(y_hexagon+sqrt(3)*3),':k')
% % plot(multiple*(x_hexagon+3*1),multiple*(y_hexagon+sqrt(3)*3),':k')
% % plot(multiple*(x_hexagon+3*-1),multiple*(y_hexagon+sqrt(3)*-3),':k')
% % plot(multiple*(x_hexagon+3*1),multiple*(y_hexagon+sqrt(3)*-3),':k')
% % plot(multiple*(x_hexagon-1.5+3*0),multiple*(y_hexagon+sqrt(3)/2+sqrt(3)*3),':k')
% % plot(multiple*(x_hexagon+1.5+3*0),multiple*(y_hexagon+sqrt(3)/2+sqrt(3)*3),':k')
% % plot(multiple*(x_hexagon-1.5+3*0),multiple*(y_hexagon+sqrt(3)/2+sqrt(3)*-4),':k')
% % plot(multiple*(x_hexagon+1.5+3*0),multiple*(y_hexagon+sqrt(3)/2+sqrt(3)*-4),':k')
% % plot(multiple*(x_hexagon+1.5+3*1),multiple*(y_hexagon+sqrt(3)/2+sqrt(3)*2),':k')
% % plot(multiple*(x_hexagon+1.5+3*-2),multiple*(y_hexagon+sqrt(3)/2+sqrt(3)*2),':k')
% % plot(multiple*(x_hexagon+1.5+3*1),multiple*(y_hexagon+sqrt(3)/2+sqrt(3)*-3),':k')
% % plot(multiple*(x_hexagon+1.5+3*-2),multiple*(y_hexagon+sqrt(3)/2+sqrt(3)*-3),':k')
% % plot(multiple*(x_hexagon+3*0),multiple*(y_hexagon+sqrt(3)*-4),':k')
% % plot(multiple*(x_hexagon+3*0),multiple*(y_hexagon+sqrt(3)*4),':k')
% % plot(multiple*(x_hexagon+3*-1),multiple*(y_hexagon+sqrt(3)*3),':k')
% % plot(multiple*(x_hexagon+3*1),multiple*(y_hexagon+sqrt(3)*3),':k')
% % plot(multiple*(x_hexagon+3*-1),multiple*(y_hexagon+sqrt(3)*-3),':k')
% % plot(multiple*(x_hexagon+3*1),multiple*(y_hexagon+sqrt(3)*-3),':k')
% % plot(multiple*(x_hexagon-1.5+3*0),multiple*(y_hexagon+sqrt(3)/2+sqrt(3)*3),':k')
% % plot(multiple*(x_hexagon+1.5+3*0),multiple*(y_hexagon+sqrt(3)/2+sqrt(3)*3),':k')
% % plot(multiple*(x_hexagon-1.5+3*0),multiple*(y_hexagon+sqrt(3)/2+sqrt(3)*-4),':k')
% % plot(multiple*(x_hexagon+1.5+3*0),multiple*(y_hexagon+sqrt(3)/2+sqrt(3)*-4),':k')
% % plot(multiple*(x_hexagon+1.5+3*1),multiple*(y_hexagon+sqrt(3)/2+sqrt(3)*2),':k')
% % plot(multiple*(x_hexagon+1.5+3*-2),multiple*(y_hexagon+sqrt(3)/2+sqrt(3)*2),':k')
% % plot(multiple*(x_hexagon+1.5+3*1),multiple*(y_hexagon+sqrt(3)/2+sqrt(3)*-3),':k')
% % plot(multiple*(x_hexagon+1.5+3*-2),multiple*(y_hexagon+sqrt(3)/2+sqrt(3)*-3),':k')
% % plot(multiple*(x_hexagon+3*-2),multiple*(y_hexagon+sqrt(3)*2),':k')
% % plot(multiple*(x_hexagon+3*-2),multiple*(y_hexagon+sqrt(3)*1),':k')
% % plot(multiple*(x_hexagon+3*-2),multiple*(y_hexagon+sqrt(3)*0),':k')
% % plot(multiple*(x_hexagon+3*-2),multiple*(y_hexagon+sqrt(3)*-1),':k')
% % plot(multiple*(x_hexagon+3*-2),multiple*(y_hexagon+sqrt(3)*-2),':k')
% % plot(multiple*(x_hexagon+3*2),multiple*(y_hexagon+sqrt(3)*2),':k')
% % plot(multiple*(x_hexagon+3*2),multiple*(y_hexagon+sqrt(3)*1),':k')
% % plot(multiple*(x_hexagon+3*2),multiple*(y_hexagon+sqrt(3)*0),':k')
% % plot(multiple*(x_hexagon+3*2),multiple*(y_hexagon+sqrt(3)*-1),':k')
% % plot(multiple*(x_hexagon+3*2),multiple*(y_hexagon+sqrt(3)*-2),':k')
%
%% bs
plot(multiple*(+3*0),multiple*(+sqrt(3)*2),'o')%1
plot(multiple*(-1.5+3*0),multiple*(+sqrt(3)/2+sqrt(3)*1),'o')%2
plot(multiple*(+3*0),multiple*(+sqrt(3)*1),'o')%3
plot(multiple*(+1.5+3*0),multiple*(+sqrt(3)/2+sqrt(3)*1),'o')%4
plot(multiple*(+3*-1),multiple*(+sqrt(3)*1),'o')%5
plot(multiple*(-1.5+3*0),multiple*(-sqrt(3)/2+sqrt(3)*1),'o')%6
plot(multiple*(+3*0),multiple*(+sqrt(3)*0),'o')%7
plot(multiple*(+1.5+3*0),multiple*(+sqrt(3)/2+sqrt(3)*0),'o')%8
plot(multiple*(+3*1),multiple*(+sqrt(3)*1),'o')%9
plot(multiple*(+3*-1),multiple*(+sqrt(3)*0),'o')%10
plot(multiple*(-1.5+3*0),multiple*(-sqrt(3)/2+sqrt(3)*0),'o')%11
plot(multiple*(+3*0),multiple*(+sqrt(3)*-1),'o')%12
plot(multiple*(+1.5+3*0),multiple*(+sqrt(3)/2+sqrt(3)*-1),'o')%13
plot(multiple*(+3*1),multiple*(+sqrt(3)*0),'o')%14
plot(multiple*(+3*-1),multiple*(+sqrt(3)*-1),'o')%15
plot(multiple*(-1.5+3*0),multiple*(-sqrt(3)/2+sqrt(3)*-1),'o')%16
plot(multiple*(+3*0),multiple*(+sqrt(3)*-2),'o')%17
plot(multiple*(+1.5+3*0),multiple*(+sqrt(3)/2+sqrt(3)*-2),'o')%18
plot(multiple*(+3*1),multiple*(+sqrt(3)*-1),'o')%19


% outer
plot(multiple*(+3*0),multiple*(+sqrt(3)*3),'ko')%20
plot(multiple*(+1.5+3*0),multiple*(+sqrt(3)/2+sqrt(3)*2),'ko')%21
plot(multiple*(+3*1),multiple*(+sqrt(3)*2),'ko')%22
plot(multiple*(+1.5+3*1),multiple*(+sqrt(3)/2+sqrt(3)*1),'ko')%23
plot(multiple*(-1.5+3*2),multiple*(-sqrt(3)/2+sqrt(3)*1),'ko')%24
plot(multiple*(+1.5+3*1),multiple*(+sqrt(3)/2+sqrt(3)*-1),'ko')%25
plot(multiple*(+1.5+3*1),multiple*(+sqrt(3)/2+sqrt(3)*-2),'ko')%26
plot(multiple*(+3*1),multiple*(+sqrt(3)*-2),'ko')%27
plot(multiple*(+1.5+3*0),multiple*(+sqrt(3)/2+sqrt(3)*-3),'ko')%28
plot(multiple*(+3*0),multiple*(+sqrt(3)*-3),'ko')%29
plot(multiple*(-1.5+3*0),multiple*(-sqrt(3)/2+sqrt(3)*-2),'ko')%30
plot(multiple*(+3*-1),multiple*(+sqrt(3)*-2),'ko')%31
plot(multiple*(+1.5+3*-2),multiple*(+sqrt(3)/2+sqrt(3)*-2),'ko')%32
plot(multiple*(+1.5+3*-2),multiple*(+sqrt(3)/2+sqrt(3)*-1),'ko')%33
plot(multiple*(+1.5+3*-2),multiple*(+sqrt(3)/2+sqrt(3)*0),'ko')%34
plot(multiple*(+1.5+3*-2),multiple*(+sqrt(3)/2+sqrt(3)*1),'ko')%35
plot(multiple*(+3*-1),multiple*(+sqrt(3)*2),'ko')%36
plot(multiple*(-1.5+3*0),multiple*(+sqrt(3)/2+sqrt(3)*2),'ko')%37
%
% % plot(multiple*(+3*0),multiple*(+sqrt(3)*4),'ko')%38
% % plot(multiple*(+1.5+3*0),multiple*(+sqrt(3)/2+sqrt(3)*3),'ko')%39
% % plot(multiple*(+3*1),multiple*(+sqrt(3)*3),'ko')%40
% % plot(multiple*(+1.5+3*1),multiple*(+sqrt(3)/2+sqrt(3)*2),'ko')%41
% % plot(multiple*(+3*2),multiple*(+sqrt(3)*2),'ko')%42
% % plot(multiple*(+3*2),multiple*(+sqrt(3)*1),'ko')%43
% % plot(multiple*(+3*2),multiple*(+sqrt(3)*0),'ko')%44
% % plot(multiple*(+3*2),multiple*(+sqrt(3)*-1),'ko')%45
% % plot(multiple*(+3*2),multiple*(+sqrt(3)*-2),'ko')%46
% % plot(multiple*(+1.5+3*1),multiple*(+sqrt(3)/2+sqrt(3)*-3),'ko')%47
% % plot(multiple*(+3*1),multiple*(+sqrt(3)*-3),'ko')%48
% % plot(multiple*(+1.5+3*0),multiple*(+sqrt(3)/2+sqrt(3)*-4),'ko')%49
% % plot(multiple*(+3*0),multiple*(+sqrt(3)*-4),'ko')%50
% % plot(multiple*(-1.5+3*0),multiple*(+sqrt(3)/2+sqrt(3)*-4),'ko')%51
% % plot(multiple*(+3*-1),multiple*(+sqrt(3)*-3),'ko')%52
% % plot(multiple*(+1.5+3*-2),multiple*(+sqrt(3)/2+sqrt(3)*-3),'ko')%53
% % plot(multiple*(+3*-2),multiple*(+sqrt(3)*-2),'ko')%54
% % plot(multiple*(+3*-2),multiple*(+sqrt(3)*-1),'ko')%55
% % plot(multiple*(+3*-2),multiple*(+sqrt(3)*0),'ko')%56
% % plot(multiple*(+3*-2),multiple*(+sqrt(3)*1),'ko')%57
% % plot(multiple*(+3*-2),multiple*(+sqrt(3)*2),'ko')%58
% % plot(multiple*(+1.5+3*-2),multiple*(+sqrt(3)/2+sqrt(3)*2),'ko')%59
% % plot(multiple*(+3*-1),multiple*(+sqrt(3)*3),'ko')%60
% % plot(multiple*(-1.5+3*0),multiple*(+sqrt(3)/2+sqrt(3)*3),'ko')%61

%% bs mat
bs(1,:)=[(multiple*(+3*0)),multiple*(+sqrt(3)*2)];%1
bs(2,:)=[(multiple*(-1.5+3*0)),multiple*(+sqrt(3)/2+sqrt(3)*1)];%2
bs(3,:)=[(multiple*(+3*0)),multiple*(+sqrt(3)*1)];%3
bs(4,:)=[(multiple*(+1.5+3*0)),multiple*(+sqrt(3)/2+sqrt(3)*1)];%4
bs(5,:)=[(multiple*(+3*-1)),multiple*(+sqrt(3)*1)];%5
bs(6,:)=[(multiple*(-1.5+3*0)),multiple*(-sqrt(3)/2+sqrt(3)*1)];%6
bs(7,:)=[(multiple*(+3*0)),multiple*(+sqrt(3)*0)];%7
bs(8,:)=[(multiple*(+1.5+3*0)),multiple*(+sqrt(3)/2+sqrt(3)*0)];%8
bs(9,:)=[(multiple*(+3*1)),multiple*(+sqrt(3)*1)];%9
bs(10,:)=[(multiple*(+3*-1)),multiple*(+sqrt(3)*0)];%10
bs(11,:)=[(multiple*(-1.5+3*0)),multiple*(-sqrt(3)/2+sqrt(3)*0)];%11
bs(12,:)=[(multiple*(+3*0)),multiple*(+sqrt(3)*-1)];%12
bs(13,:)=[(multiple*(+1.5+3*0)),multiple*(+sqrt(3)/2+sqrt(3)*-1)];%13
bs(14,:)=[(multiple*(+3*1)),multiple*(+sqrt(3)*0)];%14
bs(15,:)=[(multiple*(+3*-1)),multiple*(+sqrt(3)*-1)];%15
bs(16,:)=[(multiple*(-1.5+3*0)),multiple*(-sqrt(3)/2+sqrt(3)*-1)];%16
bs(17,:)=[(multiple*(+3*0)),multiple*(+sqrt(3)*-2)];%17
bs(18,:)=[(multiple*(+1.5+3*0)),multiple*(+sqrt(3)/2+sqrt(3)*-2)];%18
bs(19,:)=[(multiple*(+3*1)),multiple*(+sqrt(3)*-1)];%19


% outer
bs(20,:)=[(multiple*(+3*0)),multiple*(+sqrt(3)*3)];%20
bs(21,:)=[(multiple*(+1.5+3*0)),multiple*(+sqrt(3)/2+sqrt(3)*2)];%21
bs(22,:)=[(multiple*(+3*1)),multiple*(+sqrt(3)*2)];%22
bs(23,:)=[(multiple*(+1.5+3*1)),multiple*(+sqrt(3)/2+sqrt(3)*1)];%23
bs(24,:)=[(multiple*(-1.5+3*2)),multiple*(-sqrt(3)/2+sqrt(3)*1)];%24
bs(25,:)=[(multiple*(+1.5+3*1)),multiple*(+sqrt(3)/2+sqrt(3)*-1)];%25
bs(26,:)=[(multiple*(+1.5+3*1)),multiple*(+sqrt(3)/2+sqrt(3)*-2)];%26
bs(27,:)=[(multiple*(+3*1)),multiple*(+sqrt(3)*-2)];%27
bs(28,:)=[(multiple*(+1.5+3*0)),multiple*(+sqrt(3)/2+sqrt(3)*-3)];%28
bs(29,:)=[(multiple*(+3*0)),multiple*(+sqrt(3)*-3)];%29
bs(30,:)=[(multiple*(-1.5+3*0)),multiple*(-sqrt(3)/2+sqrt(3)*-2)];%30
bs(31,:)=[(multiple*(+3*-1)),multiple*(+sqrt(3)*-2)];%31
bs(32,:)=[(multiple*(+1.5+3*-2)),multiple*(+sqrt(3)/2+sqrt(3)*-2)];%32
bs(33,:)=[(multiple*(+1.5+3*-2)),multiple*(+sqrt(3)/2+sqrt(3)*-1)];%33
bs(34,:)=[(multiple*(+1.5+3*-2)),multiple*(+sqrt(3)/2+sqrt(3)*0)];%34
bs(35,:)=[(multiple*(+1.5+3*-2)),multiple*(+sqrt(3)/2+sqrt(3)*1)];%35
bs(36,:)=[(multiple*(+3*-1)),multiple*(+sqrt(3)*2)];%36
bs(37,:)=[(multiple*(-1.5+3*0)),multiple*(+sqrt(3)/2+sqrt(3)*2)];%38

bs(38,:)=[multiple*(+3*0),multiple*(+sqrt(3)*4)];%38
bs(39,:)=[multiple*(+1.5+3*0),multiple*(+sqrt(3)/2+sqrt(3)*3)];%39
bs(40,:)=[multiple*(+3*1),multiple*(+sqrt(3)*3)];%40
bs(41,:)=[multiple*(+1.5+3*1),multiple*(+sqrt(3)/2+sqrt(3)*2)];%41
bs(42,:)=[multiple*(+3*2),multiple*(+sqrt(3)*2)];%42
bs(43,:)=[multiple*(+3*2),multiple*(+sqrt(3)*1)];%43
bs(44,:)=[multiple*(+3*2),multiple*(+sqrt(3)*0)];%44
bs(45,:)=[multiple*(+3*2),multiple*(+sqrt(3)*-1)];%45
bs(46,:)=[multiple*(+3*2),multiple*(+sqrt(3)*-2)];%46
bs(47,:)=[multiple*(+1.5+3*1),multiple*(+sqrt(3)/2+sqrt(3)*-3)];%47
bs(48,:)=[multiple*(+3*1),multiple*(+sqrt(3)*-3)];%48
bs(49,:)=[multiple*(+1.5+3*0),multiple*(+sqrt(3)/2+sqrt(3)*-4)];%49
bs(50,:)=[multiple*(+3*0),multiple*(+sqrt(3)*-4)];%50
bs(51,:)=[multiple*(-1.5+3*0),multiple*(+sqrt(3)/2+sqrt(3)*-4)];%51
bs(52,:)=[multiple*(+3*-1),multiple*(+sqrt(3)*-3)];%52
bs(53,:)=[multiple*(+1.5+3*-2),multiple*(+sqrt(3)/2+sqrt(3)*-3)];%53
bs(54,:)=[multiple*(+3*-2),multiple*(+sqrt(3)*-2)];%54
bs(55,:)=[multiple*(+3*-2),multiple*(+sqrt(3)*-1)];%55
bs(56,:)=[multiple*(+3*-2),multiple*(+sqrt(3)*0)];%56
bs(57,:)=[multiple*(+3*-2),multiple*(+sqrt(3)*1)];%57
bs(58,:)=[multiple*(+3*-2),multiple*(+sqrt(3)*2)];%58
bs(59,:)=[multiple*(+1.5+3*-2),multiple*(+sqrt(3)/2+sqrt(3)*2)];%59
bs(60,:)=[multiple*(+3*-1),multiple*(+sqrt(3)*3)];%60
bs(61,:)=[multiple*(-1.5+3*0),multiple*(+sqrt(3)/2+sqrt(3)*3)];%61

bsextra=[1:19,15,16,17,5,10,15,1,2,5,9,4,1,19,14,9,17,18,19,10,11,12,18,2,6,11,16,4,3,6,10,14,8,3,2,18,13,8,4,16,12,13,14];
bs=[bs,bsextra'];
%xlim([0 1500])
%ylim([0 1500])
axis square;
axis equal;
% Enlarge figure to full screen.
%set(gcf, 'units','normalized','outerposition',[0 0 1 1]);
%% Plot users
%plot(trace(1,200,1),trace(1,200,2),'r*');

% plot(trace(1:2:200,200,1)*0.8,trace(1:2:200,200,2)*0.8,'y*');
% plot(trace(2:2:200,200,1)*0.8,trace(2:2:200,200,2)*0.8,'g*');
% plot(trace(3:2:200,200,1)*0.8,trace(3:2:200,200,2)*0.8,'r*');
end