%% CLEAR
% ####################################################################### %

clear;
close all;
clc;

%% PATHS
% ####################################################################### %

current_dir = fileparts(mfilename('fullpath'));

env_file = fullfile(current_dir, '..',  '..', '.env');
env_vars = load_env(env_file);

simulation_dir = env_vars.CPU_SIMULATION_SAVE_PATH;
plot_dir = env_vars.CPU_PLOT_BER_PATH;
functions_dir = env_vars.CPU_FUNCTIONS_PATH;

addpath(simulation_dir);
addpath(functions_dir);
addpath(plot_dir);

savefig = 1;

%% PLOTTING PARAMETERS
% ####################################################################### %

linewidth  = 2;
fontname   = 'Times New Roman';
fontsize   = 20;
markersize = 10;

colors = [0.0000 0.0000 0.0000;  % Preto
          0.0000 0.4470 0.7410;  % Azul
          0.8500 0.3250 0.0980;  % Vermelho
          0.9290 0.6940 0.1250;  % Amarelo
          0.4940 0.1840 0.5560;  % Roxo
          0.4660 0.6740 0.1880;  % Verde
          0.3010 0.7450 0.9330;  % Azul claro
          0.6350 0.0780 0.1840;  % Marrom
          0.0000 0.7500 0.7500;  % Ciano
          0.7500 0.0000 0.7500;  % Magenta
          0.7500 0.7500 0.0000;  % Ouro
          0.2500 0.2500 0.2500;  % Cinza escuro
          0.8700 0.4900 0.0000;  % Laranja queimado
          0.5000 0.5000 0.5000;  % Cinza médio
          0.0000 0.5000 1.0000;  % Azul royal
          0.5000 0.0000 0.5000]; % Roxo escuro


%% PLOT
% ####################################################################### %

e = 'ul';
decoder_type = 'MMSE';
z = '256qam';

amplifiers_type = {'IDEAL', 'SS'};
N_AMP = length(amplifiers_type);

M = 256;
K = 64;
K_f = 10;

N_BLK = 250;
A0 = [0.5, 1.0, 2.0];
N_A0 = length(A0);

B = 8;
M_QAM = 2^B;

SNR = 30;
snr = 10.^(SNR/10);

radial = 1000;
c = 3e8;
f = 1e9;
K_f_dB = 10;
K_f = 10^(K_f_dB/10);
lambda = c / f;
d = lambda / 2;
R = eye(M);

s_normalized = zeros(K, N_BLK, N_AMP, N_A0);

[x_user, y_user] = user_position_generator(K,radial);
theta_user = atan2(y_user, x_user);

A_LOS = exp(1i * 2 * pi * (0:M-1)' * 0.5 .* repmat(sin(theta_user'), M, 1));
H_LOS = sqrt(K_f / (1 + K_f)) * A_LOS;

H_NLOS = (randn(M, K) + 1i * randn(M, K)) / sqrt(2);
H = H_LOS + sqrt(1 / (1 + K_f)) * sqrtm(R) * H_NLOS;

% ####################################################################### %
%% Uplink
% ####################################################################### %

bit_array = randi([0, 1], B * N_BLK, K);
s  = (qammod(bit_array, M_QAM,'InputType','bit')).'; 
Ps = vecnorm(s,2,2).^2/N_BLK;

s_normalized = s./sqrt(Ps);

v = sqrt(0.5) * (randn(M, N_BLK) + 1i*randn(M, N_BLK));
Pv = vecnorm(v,2,2).^2 / N_BLK;
v_normalized = v./sqrt(Pv);

for a_idx = 1:N_A0
    for amp_idx = 1:N_AMP

        a0 = A0(a_idx);
        current_amp_type = amplifiers_type{amp_idx};

        y = H * sqrt(snr) * amplify_signal(s_normalized, current_amp_type, a0) + v_normalized;

        decoder = decode_signal(decoder_type, H, snr);
        s_hat = decoder * y;
        Ps_hat = vecnorm(s_hat,2,2).^2/N_BLK;
        s_hat_normalized(:,:,amp_idx,a_idx) = s_hat.*sqrt(Ps./Ps_hat);
    end
end

% ####################################################################### %
%% Downlink
% ####################################################################### %
% 
% b = randi([0 1], N_BLK*B,K);
% s  = (qammod(b, M_QAM,'InputType','bit')).';
% Ps = vecnorm(s,2,2).^2/N_BLK;
% s_normalized = s./sqrt(Ps);
% eta = 1/K;
% 
% precoder = sqrt(M-K) * (conj(H) / (H.' * conj(H)));
% x = precoder*sqrt(eta)*s_normalized;
% %x = precoder(:,:,snr_idx)*sqrt(eta)*s_norm;
% 
% v = sqrt(0.5)*(randn(K,N_BLK) + 1i*randn(K,N_BLK));
% Pv = vecnorm(v,2,2).^2/N_BLK;
% v_norm = v./sqrt(Pv);
% 
% for a_idx = 1:N_A0
%     for amp_idx = 1:N_AMP
%         a0 = A0(a_idx);
%         current_amp_type = amplifiers_type{amp_idx};
% 
%         y = H.' * sqrt(snr) * amplify_signal(x, current_amp_type, a0) + v_norm;
% 
%         s_hat = y;
%         Ps_hat = vecnorm(s_hat,2,2).^2/N_BLK;
%         s_hat_normalized(:,:,amp_idx,a_idx) = s_hat.*sqrt(Ps./Ps_hat);
%     end
% end

% ####################################################################### %
%% PLOTAGEM DA CONSTELAÇÃO
% ####################################################################### %

figure;
set (gcf, "Position", [0, 0, 800, 600]);

%subplot(2,2,1)
plot(real(s_hat_normalized(:,:,1,1)), imag(s_hat_normalized(:,:,1,1)),'.','MarkerSize', markersize,'Color',colors(2, :));
hold on;
plot(real(s_hat_normalized(:,:,2,1)), imag(s_hat_normalized(:,:,2,1)),'.','MarkerSize', markersize,'Color',colors(3, :));
xlabel('I', 'FontName', fontname, 'FontSize', fontsize);
ylabel('Q', 'FontName', fontname, 'FontSize', fontsize);
set(gca, 'FontName', fontname, 'FontSize', fontsize);
hold off;

graph_name = sprintf('constellation_%s_%s_%d_%d_%s_05a', e, lower(decoder_type), M, K, z);

if savefig == 1
    saveas(gcf,[plot_dir graph_name],'epsc2');
    saveas(gcf,[plot_dir graph_name],'png');
end

%subplot(2,2,2)
plot(real(s_hat_normalized(:,:,1,1)), imag(s_hat_normalized(:,:,1,1)),'.','MarkerSize', markersize,'Color',colors(2, :));
hold on;
plot(real(s_hat_normalized(:,:,2,2)), imag(s_hat_normalized(:,:,2,2)),'.','MarkerSize', markersize,'Color',colors(4, :));
xlabel('I', 'FontName', fontname, 'FontSize', fontsize);
ylabel('Q', 'FontName', fontname, 'FontSize', fontsize);
set(gca, 'FontName', fontname, 'FontSize', fontsize);
hold off;

graph_name = sprintf('constellation_%s_%s_%d_%d_%s_10a', e, lower(decoder_type), M, K, z);

if savefig == 1
    saveas(gcf,[plot_dir graph_name],'epsc2');
    saveas(gcf,[plot_dir graph_name],'png');
end

%subplot(2,2,3)
plot(real(s_hat_normalized(:,:,1,1)), imag(s_hat_normalized(:,:,1,1)),'.','MarkerSize', markersize,'Color',colors(2, :));
hold on;
plot(real(s_hat_normalized(:,:,2,3)), imag(s_hat_normalized(:,:,2,3)),'.','MarkerSize', markersize,'Color',colors(5, :));
xlabel('I', 'FontName', fontname, 'FontSize', fontsize);
ylabel('Q', 'FontName', fontname, 'FontSize', fontsize);
set(gca, 'FontName', fontname, 'FontSize', fontsize);
hold off;

graph_name = sprintf('constellation_%s_%s_%d_%d_%s_20a', e, lower(decoder_type), M, K, z);

if savefig == 1
    saveas(gcf,[plot_dir graph_name],'epsc2');
    saveas(gcf,[plot_dir graph_name],'png');
end