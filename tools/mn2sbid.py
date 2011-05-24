#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
Script para renomeação dos diretórios contendo os eBooks

O script deve ser executado no diretório que contém todas as pastas de livros

"""
import os

referencias = [
    ['w2', '9788523204716', 'arg_tra_cal'] ,
    ['vm', '9788523205553', 'alm_fes_uma_cid'] ,
    ['v9', '9788585676124', 'vig_ali_nut_lim_int_red_sau'] ,
    ['tv', '9788575411025', 'rec_cri'] ,
    ['th', '9788585676032', 'pri_mos_imp_san_bra'] ,
    ['t7', '9788585676094', 'osw_cruz_con_mito_cie_bra'] ,
    ['sp', '9788575410837', 'cen_pos_exp_des_mes_pro_sau_col'] ,
    ['sd', '9788575410172', 'cam_sau_pub_bra'] ,
    ['s6', '9788523206369', 'um_rig_out'] ,
    ['rq', '9788523205874', 'tut_bah'] ,
    ['r9', '9788523205638', 'tra_cen_tra'] ,
    ['qk', '9788523205669', 'toxicomanias'] ,
    ['q5', '9788523206208', 'ris_rad_vig_san'] ,
    ['p5', '9788523205966', 'por_afr_bra'] ,
    ['nq', '9788523206093', 'pod_cam'] ,
    ['nb', '9788523205898', 'pen_dis_web'] ,
    ['n2', '9788523205621', 'mes_cap_fam_bah'] ,
    ['mn', '9788523205935', 'histerosalpingografia'] ,
    ['m9', '9788523205584', 'fic_esc'] ,
    ['kv', '9788571397729', 'uni_cri'] ,
    ['kd', '9788571397842', 'trajetorias'] ,
    ['k4', '9788571395800', 'ser_nob_col'] ,
    ['jg', '9788571397804', 'rum_cet'] ,
    ['hv', '9788571398818', 'patricios'] ,
    ['hm', '9788571399099', 'out_his_edu'] ,
    ['gv', '9788571393370', 'int_log'] ,
    ['gh', '9788571399242', 'gen_neg_par_oit_pop_fam_par_esp'] ,
    ['g5', '9788571391284', 'esc_hom_nov_ent_ilu_rev_fra'] ,
    ['fs', '9788523204952', 'faz_diz_cor'] ,
    ['fm', '9788523204242', 'enc_sua_san'] ,
    ['f7', '9788523204006', 'mod_ate_sau'] ,
    ['ds', '9788523203856', 'inf_afro'] ,
    ['db', '9788523203986', 'his_sal_nom_sua_rua'] ,
    ['cp', '9788523203023', 'que_tem_med_ger_sho'] ,
    ['cb', '9788523206772', 'for_pro'] ,
    ['bk', '9788523205386', 'esp_cul'] ,
    ['9q', '9788523205430', 'esc_nar_sob_ali_cul'] ,
    ['97', '9788523205157', 'do_ref_lut_arm'] ,
    ['8p', '9788571398320', 'abolicao'] ,
    ['7x', '9788571399273', 'abelhas'] ,
    ['75', '9788571393929', 'a_bei_lin_for_urb_nor_pau'] ,
    ['6q', '9788523206253', 'don_can'] ,
    ['68', '9788523206192', 'dif_cul_cie'] ,
    ['5w', '9788523206277', 'edu_inc'] ,
    ['5h', '9788523205744', 'die_mos_sao_ben_bah'] ,
    ['4r', '9788523206307', 'con_uni_bai'] ,
    ['48', '9788523206031', 'africa_a_vista'] ,
    ['3q', '9788523205614', 'ava_e_soc'] ,
    ['3k', '9788575410172', 'cam_sau_pub_bra'] ,
    ['36', '9788523203528', 'ava_em_sau'] ,
    ['q', '9788575411377', 'tra_per_ant_ali_nut_soc_ind_ama'] ,
    ['4', '9788575410066', 'his_soc_tub_tub_1900-1950']
]

abspath = os.path.abspath('.')

for sbid, isbn, orig in referencias: 
    try:
        """ Primeiro: renomeando os arquivos completos (*_full.pdf) para <isbn>.pdf """
        original_file = os.path.join(orig, 'pdf/'+orig+'_full.pdf')
        future_file = os.path.join(orig, 'pdf/'+isbn+'.pdf')         
        os.rename(original_file, future_file)
    except IOError:
        print 'arquivo %s nao renomeado' % (orig)   
         
    try:
        """ Segundo: renomeando as pastas de mnemonicos para <sbid> """    
        os.rename(orig, sbid)
    except IOError:
        print 'diretorio %s nao renomeado'
    
    try:
        """ Terceiro: Criando o diretorio ./cover/original """
        new_dir = os.path.join(sbid, 'cover/original' ) 
        os.makedirs(new_dir)
    except IOError:
        print 'diretorio cover/original nao criado para %s' % (sbid)
    
        

