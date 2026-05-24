function [H] = rician_channel_generator(M , K , K_f)
    
    H_LOS = ones(M, K);
    H_NLOS = (randn(M, K) + 1i * randn(M, K)) / sqrt(2);
    H = sqrt(K_f / (1 + K_f)) * H_LOS + sqrt(1 / (1 + K_f)) * H_NLOS;
end