#!/usr/local/python2.4/bin/python
# -*- coding: utf-8 -*-

import MySQLdb, sys, time, re, glob, os
import flybase32

from flybase32 import tranking, gsedit, gslogin

'''開啟寫入資料庫，寫入stdcdr、stdcdr.stk、cdrnotpass'''
do_db = 1
'''
使用step 6 的哪一個
1. 製作成flybase格式
2. 匯入資料庫
'''
use_step6 = 2
'''資料庫位置'''
dbpath = '/opt/fb32/db/'
'''7. 假如有flybase格式，就匯入  0 or 1'''
load_flybase=0

'''測試幾筆 數字'''
testmaxnum = None

'''主機資訊'''

#hostname='203.70.68.120'
hostname='140.118.33.1'
port1=3306
user1={'etd_available': 'etd_available','etd_submitted':'etd_submitted'}
passwd1={'etd_available' : 'etdava99','etd_submitted':'etdsub99'}

cdrnotpasspath='cdrnotpass'
#table_name = {'etd_available': 'stdcdr','etd_submitted': 'stdcdr.stk'}
table_name = {'etd_available': 'test','etd_submitted': 'test.stk'}
# table_name = {'etd_available': 'stdcdr'}

sorttable = ['etd_available','etd_submitted']

dictablelist = {'etd_available':'sql_to_flybase_available.ini','etd_submitted':'sql_to_flybase_submitted.ini'}
# dictablelist = {'etd_available':'sql_to_flybase_available.ini'}

non_fld = {'pyr':'-','sc':'國立臺灣科技大學','add':'-','tel':'-','byr':'-','sayc':'-','third':'-'}

## 暫存檔遇到同一筆不跳過
stk_not_continue = 0

## 用於更新暫存檔已經轉到正式資料庫的差異
stk_turn_official = []

def main():
    # 連接到 MySQL
    ## port 3306
    #db = MySQLdb.connect(host="203.70.68.120", user="totoro", passwd="2054043", db="etd_available",port=3366,charset="utf8")
    for dd in sorttable:
        dic_table, dic_data = set_dic(dictablelist[dd])
        pslog("Step 0: Start at %s" % dd)
        print "Start"
        pslog("Dictionary",dic_data)
        
        db = MySQLdb.connect(host=hostname, user=user1[dd], passwd=passwd1[dd], db="%s" % dd,port=port1)
        cursor = db.cursor()
        
        ## 所有sql id
        all_urn = []
        ## 轉flybase格式的暫存dic
        tmpdata = {}
        second_table = ['filename_by_urn','keyword_by_sid','keyword_c_by_sid','advisor_by_urn','etd_main'] ## 取資料的table
        # 執行 SQL 語句
        #cursor.execute("SET NAMES utf8;")
        ''' 1. 取得sql的所有論文編號 '''
        print "Wait."
        pslog("Step 1: Get all sql urn")
        cursor.execute("select * from etd_main;")
        result = cursor.fetchall()
        pslog('Total num',len(result),lv=1)
        for record in result[:testmaxnum]:
            all_urn.append(strtoutf8(record[0]))
            tmpdata[strtoutf8(record[0])] = {}
            
        ''' 2. 取得關鍵字(keyword_by_urn):keyword (keyword_c_by_urn):keyword_c '''
        
        pslog("Step 2: Get all keyword")
        ## 英文關鍵字
        chang_dic(tmpdata,cursor,'urn,keyword,timestamp','keyword_by_urn','kwe')
        ## 中文關鍵字
        chang_dic(tmpdata,cursor,'urn,keyword_c,timestamp','keyword_c_by_urn','kwc')
        
        ''' 3. 取得指導教授、口試委員(advisor_by_urn): '''
        
        pslog("Step 3: Get all advisor")
        cursor.execute("SELECT urn,advisor_name_c,advisor_title,advisor_email,timestamp,advisor_name,advisor_title_c,ensure FROM advisor_by_urn;")
        result = cursor.fetchall()
        for record in result[:testmaxnum]:
            urn = strtoutf8(record[0])
            if not tmpdata.has_key(urn): continue
            tdata = tmpdata[urn]
            '''Adviser:指導教授、Advisory Committee:委員'''
            '''
            英文欄位需過慮&#8208;
            '''
            ad_to_fld= {'Adviser':['adc','ade'],'Advisory Committee':['sayc','saye'],'Dean of Graduate Sch':['sayc','saye'],'Head of Department':['sayc','saye']}
            try:
                fldc , flde = ad_to_fld[strtoutf8(record[2])]
            except:
                print "Something wrong at %s ,and value is %s"  % ('Step 3',strtoutf8(record[2]))
                pslog("Something wrong at %s ,and value is %s"  % ('Step 3',strtoutf8(record[2])))
                import traceback
                print traceback.format_exc()
                return
            ## 處理多個指導教授跟口試委員
            if tdata.has_key(fldc):
                fldcl = tdata[fldc]
                fldcl.append(strtoutf8(record[1]))
                #del tdata[fldc]
                tdata[fldc] = fldcl
            else:
                tdata[fldc] = [strtoutf8(record[1])]
            if tdata.has_key(flde):
                fldel = tdata[flde]
                fldel.append(strtoutf8(record[5]).replace('&#8208;',''))
                #del tdata[flde]
                tdata[flde] = fldel
            else:
                tdata[flde] = [strtoutf8(record[5])]
                
            ##取得email
            if fldc == 'adc':
                ademl = tdata.get('adem',[])
                ademl.append(strtoutf8(record[3]))
                tdata['adem'] = ademl
            tmpdata[urn] = tdata
            
            ## 取得教授是否同意授權
            if record[7]:
                ## 蔡XX-指導教授-chlin@mail.ntust.edu.tw–已同意著作權歸屬選項
                adctil = {'Adviser':'指導教授','Advisory Committee':'口試委員'}
                adctin = adctil[strtoutf8(record[2])]
                owncheck = "%s-%s-%s–@chang@著作權歸屬選項" % (fldc,adctin,tdata['adem'])
                if strtoutf8(record[7]) == 'Y':
                    owncheck = owncheck.replace('@chang@','同意')
                elif strtoutf8(record[7]) == 'N':
                    owncheck = owncheck.replace('@chang@','同意')
                else:
                    owncheck = ''
                    
                if owncheck:
                    if tdata.has_key('owncheck'):
                        tt = tdata['owncheck']
                        tt.append(owncheck)
                        tdata['owncheck'] = tt
                    else:
                        tdata['owncheck'] = [owncheck]
            
            ## sayd， 已經有sayd欄位了
            # if not tdata.has_key('sayd'):
                # tdata['sayd'] = str(record[4]).replace('-','/').split(' ')[0].strip()
        
        ''' 4. 取得論文檔案全文資料SQL(filename_by_urn):filename、timestamp FLY'''
        
        pslog("Step 4: Main")
        cursor.execute("SELECT A.* , B.* FROM  etd_main AS A LEFT JOIN filename_by_urn AS B ON A.urn = B.urn")
        result = cursor.fetchall()
        num=0
        for record in result[:testmaxnum]:
            num += 1
            print "%s/%s" % (num,len(result))
            ## 送審日期，最後有ID再寫入
            verifytime = []
            ## 審核不通過原因
            notpass_reason = ''
            ## 校內校外開放時間是基於sdate
            opauth_basedate = ''
            availability = ''
            ## flybase id
            dbid = ''
            for r in range(0,len(record)):
                if dic_data.has_key('etd_main_%s'%r):
                    if dic_data['etd_main_%s'%r] == 'flybaseid':
                        s = strtoutf8(record[r]).split('@')[0].upper()
                        dbid = 'G'+'0'*(10-len(s))+s
                        dbid = dbid.replace(' ','')
            if not dbid:
                wf = open('no_sid.txt','a')
                print >> wf , urn
                wf.close()
                continue
            ''' 把寫入的dbid記錄下來，因為有漏'''
            wf = open('write_dbid.txt','a')
            print >> wf , dbid
            wf.close()
            ''' 確認 id 是否有被寫入過 '''
            db = flybase32.fbopen('/opt/fb32/db/%s'%table_name[dd])
            rls = db.query('id="%s"'%dbid)
            if len(rls) == 1:
                ## 有寫過就跳過不做這一筆
                if dd == table_name['etd_submitted']:
                    stk_not_continue = 1
                else:
                    continue
            else:
                wf = open('not_write.txt','a')
                print >> wf , urn
                wf.close()
                if dd == table_name['etd_available']:
                    stk_turn_official.append(dbid)
            
            ''' stdcdr will add'''
            sf = open('stdcdr_will_add.txt','a')
            print >> sf, dbid
            sf.close()
            
            ## sql urn
            urn = strtoutf8(record[0])
            print urn
            try:
               tdata = tmpdata[urn]
            except:
                continue
            val = ''
            for r in range(len(record)):
                if dic_data.has_key('etd_main_%s'%r):
                    # wff = open('test.txt','a')
                    # print >> wff,strtoutf8(record[r])
                    # wff.close()
                    if not strtoutf8(record[r]):
                        tt = '-'
                    else:
                        tt = strtoutf8(record[r])
                    ## some field have to do something extra，有一些要做額外的事情
                    fld = dic_data['etd_main_%s'%r]
                    if fld == "ancl":
                        val = strtoutf8(record[r])
                        tt = "同意"
                    if fld == "ancld":
                        '''
                            withheld 國家圖書館 -20xx 年後公開
                            unrestricted 國家圖書館立即開放
                            notavailable 國家圖書館不開放
                        '''
                        if val == 'notavailable':
                            tt = '不公開'
                            tdata['authstatus3'] = '99'
                        elif val == 'unrestricted':
                            ## 校內校外開放時間是基於sdate，所以國圖的時間也使用這個
                            tt = opauth_basedate
                            tdata['authstatus3'] = '0'
                        elif val == 'withheld':
                            tt = str(tt).replace('-','/')
                            # print "tt=%s" % tt
                            # print "opauth_basedate=%s"% opauth_basedate
                            # pslog("tt=%s" % tt)
                            # pslog("opauth_basedate=%s"% opauth_basedate)
                            try:
                                tdata['authstatus3'] = str(int(tt.split('/')[0])-int(opauth_basedate.replace('-','/').split('/')[0]))
                            except:
                                tdata['authstatus3'] = '-'
                        else:
                            print "Something wrong at %s,and the value is %s" % (fld,tt)
                            pslog("Something wrong at %s,and the value is %s" % (fld,tt))
                            return
                    if fld in ["popen",'verifytime','cdt','sayd','edf','ancld']:
                        ## 需要把日期 '-' 換成 '/'
                        tt = str(tt).replace('-','/')
                        if tt.find(' ')!=-1:
                            tt = tt.split(' ')[0]
                    if fld == "verifytime":
                        ## 提交日期，寫入cdrnotpass verifytime欄位
                        verifytime.append(tt)
                        opauth_basedate = tt
                        ## 校內校外授權
                        '''
                        unrestricted:校內外完全公開
                        restricted:校內公開 校外永不公開
                        withheld:校內外均1年後公開
                        not_available:校內外均不公開
                        off_campus_withheld:校內立即公開 校外1年後公開
                        campus_withheld:校內1年後公開 校外不公開
                        notfulltext:沒有全文
                        user_define:使用者自訂
                        '''
                        ## 根據opauth_basedate往後延長幾年
                        #authstatus1、authstatus2
                        tt = tt.split('/')
                        ava_to_fld = {'unrestricted':['0','0'],'restricted':['0','99'],'withheld':['1','1'],'not_available':['99','99'],'off_campus_withheld':['0','1'],'campus_withheld':['1','99'],'notfulltext':['X','X']}
                        if availability == 'user_define':
                            if dd == 'etd_submitted':
                                ava_to_fld['user_define'] = [strtoutf8(record[38]),strtoutf8(record[39])]
                            elif dd == 'etd_available':
                                ava_to_fld['user_define'] = [strtoutf8(record[37]),strtoutf8(record[38])]
                        authstatus1 ,authstatus2 = ava_to_fld[availability]
                        if authstatus1 == 'X':
                            op = '-'
                            auth = '-'
                            authstatus1 = '-'
                            authstatus2 = '-'
                        else:
                            op = authstatus1 == '0' and opauth_basedate or authstatus1 == '99' and '不公開' or "%s/%s/%s" % (int(tt[0])+int(authstatus1),tt[1],tt[2])
                            auth = authstatus2 == '0' and opauth_basedate or authstatus2 == '99' and '不公開' or "%s/%s/%s" % (int(tt[0])+int(authstatus2),tt[1],tt[2])
                        tdata['op'] = op
                        tdata['auth'] = auth
                        tdata['authstatus1'] = authstatus1
                        tdata['authstatus2'] = authstatus2
                        continue
                    if fld == 'cdrnotpass':
                        ## 寫入審核不通過原因
                        notpass_reason = tt.replace('\n','').strip().replace(' ','')
                        continue
                    if fld == 'cdt':
                        write_cdrnopass(dbid,'tranintotime',tt,just_write=1)
                    if fld == 'flybaseid':
                        ## 用學校email 開頭當做學號
                        tdata['sid'] = tt.split('@')[0].upper()
                        # s = tt.split('@')[0].upper()
                        # dbid = 'G'+'0'*(10-len(s))+s
                        tdata['dbid'] = dbid
                        continue
                    if fld == '審核通過':
                        ## 帶修改
                        write_cdrnopass(dbid,'verifydonetime',tt)
                        #print "%s:%s" % (fld,tt)
                        continue
                    if fld == '修改時間':
                        #print "%s:%s" % (fld,tt)
                        if tt != '-':
                            log = []
                            logl = tt.split('<br>')
                            for ls in logl:
                                if ls:
                                    logstr ,times = cut_the_time(ls)
                                    log.append(logstr)
                            if tdata.has_key('log'):
                                log.append(tdata['log'])
                                #del tdata['log']
                                tdata['log'] = log
                            else:
                                tdata['log'] = log
                        continue
                    if fld in ['log']:
                        ## 需要略過的 fld
                        print "%s:%s" % (fld,tt)
                        continue
                    if fld =='availability':
                        availability = tt
                        continue
                    if fld == 'own':
                        '''a為僅作者(學生)所有，b為作者(學生)和教授共同擁有，0則是顯示未設定'''
                        if tt != '-':
                            # adc = tdata['adc']
                            # own = ''
                            if tt == 'a': tt = '僅作者擁有'
                            elif tt == 'b': tt = '作者與指導教授共同擁有'
                            elif tt == '0':
                                # own = ''
                                tt = '-'
                            else:
                                print "Something wrong in %s , and tt is %s" % (fld,tt)
                                pslog("Something wrong in %s , and tt is %s" % (fld,tt))
                                return
                            # if own:
                                # tt = ["%s:%s" % (adcna,own) for adcna in adc]
                    if fld == 'ses':
                        if tt == '1':
                            dt = int(tdata['yr']) + 1911
                        else:
                            dt = int(tdata['yr']) + 1912
                        tdata['byr'] = str(dt)
                    if fld == 'verify':
                        if tt == 'NO':
                            continue
                        elif tt == 'YES':
                            tt = 'pass'
                        else:
                            print "Somnthing wrong in verify,and value is %s" % tt
                            return
                    if fld == 'ok':
                        tt = tt and tt.lower() or '-'
                    if fld == '著作確認':
                        if not tt == '-' :
                            nextdo = 0
                            for ll in tt.split('\n'):
                                if nextdo == 1 :
                                    # print 'here have wrong2,',ll
                                    ll = ll.split('-')
                                    adc = ll[2].strip()
                                    own = ll[3].find('不同意') != -1 and '僅作者擁有' or '作者與指導教授共同擁有'
                                    if tdata.has_key('own'):
                                        # tstr = tdata['own']
                                        # tstr.append('%s:%s'%(adc,own))
                                        #del tdata['own']
                                        tdata['own'] = own
                                    else:
                                        tdata['own'] = ['%s:%s'%(adc,own)]
                                    nextdo = 0
                                    continue
                                if ll.find('著作權確認：') != -1 and len(ll.split('-')) > 1:
                                    # print 'here have wrong1,',ll
                                    ll = ll.split('-')
                                    adc = ll[2].strip()
                                    own = ll[3].find('不同意') != -1 and '僅作者擁有' or '作者與指導教授共同擁有'
                                    if tdata.has_key('own'):
                                        # tstr = tdata['own']
                                        # tstr.append('%s:%s'%(adc,own))
                                        #del tdata['own']
                                        tdata['own'] = own
                                    else:
                                        tdata['own'] = ['%s:%s'%(adc,own)]
                                elif ll.find('著作權確認：') != -1 and len(ll.split('-')) == 1:
                                    nextdo = 1

                        continue
                    ## 在這新增
                    if fld.find('/') != -1:
                        for fl in fld.split('/'):
                            if fl in ['lg','langdisp']:
                                if tt == 'Chi':
                                    ll = {'lg':"中文",'langdisp':'tw'}
                                if tt == "Eng":
                                    ll = {'lg':"英文",'langdisp':'en'}
                                tdata[fl] = ll[fl]
                            else:
                                tdata[fl] = tt
                        continue
                    if tdata.has_key(fld) and tdata[fld]:
                        ## 針對英文名字的方式
                        tt = "%s %s" % (tdata[fld],tt)
                        #del tdata[fld]
                        tdata[fld] = tt
                    else:
                        tdata[fld] = tt
            ''' 補充應該要輸入的地方 '''
            if table_name[dd] == table_name['etd_available']:
                tdata['fuok'] = 'yes' # 全文檔狀態
                tdata['ok'] = 'yes' # 是否建檔完成
                tdata['verify'] = 'pass' # 審核通過
                cost_num = 0
            elif table_name[dd] == table_name['etd_submitted']:
                cost_num = 1
            if strtoutf8(record[45]) and strtoutf8(record[45]) != 'None':
                tdata['fd'] = '電子全文'
                tdata['fu'] = "%s/%s" % (strtoutf8(record[47-cost_num]),strtoutf8(record[46-cost_num]))
                tdata['fuok'] = 'yes' # 全文檔狀態
                tdata['ok'] = 'yes' # 是否建檔完成
                upldtime = strtoutf8(record[49-cost_num]).replace('-','.')
                tt = upldtime.split(' ')[0].split('.')
                upldtime = "Y%s.M%s.D%s %s" % (tt[0],tt[1],tt[2],upldtime.split(' ')[1])
                tlog = "M FullText_Upload %s %s" % (upldtime,tdata['sid'])
                log = []
                if tdata.has_key('log'):
                    log += tdata['log']
                    #del tdata['log']
                log.append(tlog)
                tdata['log'] = log
            # 範例:SQL:2005-06-10 10:34:17
            # 範例:M admin Y2016.M8.D26 18:28 203.70.68.6
            
            ''' 5. 補上沒有的欄位'''
            
            #pslog("Step 5: Something field lost")
            tdata_fld = tdata.keys()
            for fld in non_fld:
                if fld not in tdata_fld:
                    tdata[fld] = non_fld[fld]
                    
            ''' 5.1 有可能是舊系所，如"高分子系" '''
            
            dp = tdata['dp']
            print dp
            dpdb = flybase32.fbopen('%scdrindp'%dbpath)
            rls = dpdb.query('"%s"'%dp)
            if len(rls) == 1:
                if not dp == dpdb[rls[0],'dp',0]:
                    tdata['odp'] = dp
                    tdata['dp'] = dpdb[rls[0],'dp',0]
            else:
                print "Something wrong in 5.1,and the value is %s" % dp
                tdata['dp'] = '測試系所'
                #return
            
            ''' 5.2 補上學院名稱 '''
            
            dp = tdata['dp']
            dpdb = flybase32.fbopen('%scdrindp'%dbpath)
            rls = dpdb.query('dp="%s"'%dp)
            if len(rls) == 1:
                tdata['in'] = dpdb[rls[0],'in',0]
                tdata['ein'] = dpdb[rls[0],'ein',0]
            elif len(rls) == 0:
                wf = open('cdrindp_notexist_dp.txt','a')
                print >> wf , dp
                wf.close()
            del dpdb
            
            ''' 測試 show tdata'''
            
            # wff = open('test.txt','a')
            # for r in tdata:
                # print >>wff,"r:%s:%s" % (type(tdata[r]),tdata[r])
            # wff.close()
            
            ''' 6-1. 製作成flybase格式'''
            if use_step6 == 1:
                #pslog("Step 6-1: Make flybase format")
                format_flybase(tdata,table_name[dd],str(num/1000))
            
            ''' 6-2. 匯入資料庫'''
            if use_step6 == 2:
                #pslog("Step 6-2: Make a new one")
                if do_db:
                    tdata['id'] = tdata['dbid']
                    del tdata['dbid']
                    ## 移除'-'
                    for r in tdata:
                        if tdata[r] == '-':
                            tdata[r] = ''
                    db = flybase32.fbopen('%s%s'%(dbpath,table_name[dd]),'c')
                    db.lock()
                    if stk_not_continue:
                        db[tdata['id']] = tdata
                        stk_not_continue = 0
                    else:
                        db.new(tdata)
                    db.unlock()
                    del db
                
            ''' 8. 匯入論文不通功過原因 cdrnotpass，送審時間 '''
            
            # pslog("Step 8: Input database of cdrnotpass")
            if verifytime and num > 17126:
                ## verifytime=論文送審時間
                write_cdrnopass(dbid,'verifytime',verifytime,just_write=1)
                pass
            if notpass_reason and num > 17126:
                ## rtime=審核不通過時間、reason=審核不通過時間、raccount=退審人員
                write_cdrnopass(dbid,'reason',notpass_reason,just_write=1)
                write_cdrnopass(dbid,'rtime','unknown',just_write=1)
                write_cdrnopass(dbid,'raccount','unknown',just_write=1)
                pass
            ''' 9. 匯入隱藏摘要 cdrpostponed '''
            '''沒有摘要需要隱藏'''
            
            ''' 10. 刪除tmpdata裡的資料釋放記憶體 '''
            del tmpdata[urn]
            
        '''7. 假如有flybase格式，就匯入'''
        if load_flybase:
            fl = glob.glob('%s/%s_*.txt'%('/opt/fb32/db/readsql',table_name[dd]))
            for fn in fl:
                print 'cd %s;fb3load -d %s %s'%(dbpath,table_name[dd],fn)
                ll = os.popen('cd %s;fb3load -d %s %s'%(dbpath,table_name[dd],fn))
                print ll.read()
                if ll.read().find('errors') != -1:
                    break
            
        ''' Special: 更新資料時用，刪除已經更新到正式端的暫存檔資料'''
        if dd == table_name['etd_submitted'] and stk_turn_official:
            db = flybase32.fbopen('%s%s'%(dbpath,table_name[dd]),'c')
            wf = open('stk_will_kill_id.txt','w')
            print >> wf,"\n".join(stk_turn_official)
            wf.close()
            db.lock()
            for dbid in stk_turn_official:
                del db[dbid]
            db.unlock()
            del db
            
        
        pslog("Step : End at %s" % dd)
        # 輸出結果
        # wf = open('test.txt','a')
        # for r in tmpdata:
            # if tmpdata[r]:
                # print >> wf , "%s:%s" % ('id',tmpdata[r]['id'])
                # for re in tmpdata[r]:
                    # if re == 'id':continue
                    # print >> wf , "%s:%s" % (re,tmpdata[r][re])
                # print >> wf , "/"
        # wf.close()

def cut_the_time(ls):
    ## 把雙空格改成單空格
    ls = ls.replace('  ',' ')
    ''' 參考
修改時間/帳號/IP：Wed Aug  3 16:42:08 CST 2005 / chinhl / 140.118.33.110
<br>修改時間/帳號/IP：Wed Aug  3 16:42:29 CST 2005 / chinhl / 140.118.33.110
<br>
    '''
    # 範例:M admin Y2016.M8.D26 18:28 203.70.68.6
    wk = {'Jan':'01','Feb':'02','Mar':'03','Apr':'04','May':'05','Jun':'06','Jul':'07','Aug':'08','Sep':'09','Oct':'10','Nov':'11','Dec':'12'}
    ls = ls.split('：')[1].split('/')
    tt = ls[0].strip().split(' ')
    logstr = "M %s Y%s.M%s.D%s %s %s" % (ls[1].strip(),tt[5],wk[tt[1]],tt[2],tt[3],ls[2].strip())
    times = "%s/%s/%s %s" % (tt[5],wk[tt[1]],tt[2],tt[3])
    return logstr,times
    
def write_cdrnopass(dbid,fld,times,just_write=0):
    db = flybase32.fbopen("%s%s" % (dbpath,cdrnotpasspath),'c')
    rls = db.query('id=%s'%dbid)
    if not times or times == '-':return
    if type(times) != list: timel = [i for i in times.split('<br>') if i]
    '''修改時間/帳號/IP：Fri Jul 29 15:54:13 CST 2005 / chinhl / 140.118.33.110\n<br>修改時間/帳號/IP：Fri Jul 29 15:54:20 CST 2005 / chinhl / 140.118.33.110\n<br>'''
    if len(rls) == 1:
        if just_write:
            trantime = db[rls[0],fld]
            if type(times) == list:
                trantime += times
            else:
                trantime.append(times)
            if do_db:
                db.lock()
                db[rls[0],fld] = trantime
                db.unlock()
        else:
            donetimes = db[rls[0],fld]
            for ls in timel:
                logstr ,times = cut_the_time(ls)
                donetimes += times
            if do_db:
                db.lock()
                db[rls[0],fld] = donetimes
                db.unlock()
    else:
        tdata = {}
        tdata['id'] = dbid
        if just_write:
            if type(times) == list:
                tdata[fld] = times
            else:
                tdata[fld] = [times]
            if do_db:
                db.lock()
                db.new(tdata)
                db.unlock()
        else:
            donetimes = []
            for ls in timel:
                logstr ,times = cut_the_time(ls)
                donetimes += times
            tdata[fld] = donetimes
            if do_db:
                db.lock()
                db.new(tdata)
                db.unlock()
    del db

def chang_dic(tmpdata,cursor,sql_fld,tb,fld):
    cursor.execute("select %s from %s;" % (sql_fld,tb))
    result = cursor.fetchall()
    for record in result:
        if strtoutf8(record):
            '''
            sql fld:
            urn:keyword:timestamp
            '''
            urn = strtoutf8(record[0])
            if tmpdata.has_key(urn):
                tdata = tmpdata[urn]
                if tdata.has_key(fld) and tdata[fld]:
                    tt = tdata[fld]
                    tt.append(strtoutf8(record[1]))
                    #del tdata[fld]
                    tdata[fld] = tt
                else:
                    tdata[fld] = [strtoutf8(record[1])]
                #del tmpdata[urn]
                tmpdata[urn] = tdata
    ## 如果有urn但是沒有關鍵字的話
    for dd in tmpdata:
        if not tmpdata[dd].has_key(fld):
            tmpdata[dd][fld] = '-'
    
def format_flybase(dic,fly,num):
    # 輸出 flybase 格式
    import codecs
    wf = open('%s_%s.txt' % (fly,num),'a')
    print >> wf , "%s %s" % ('id',dic['dbid'])
    dbid = dic['dbid']
    for r in dic:
        #print "r:%s  =>  %s" % (r,dic[r])
        if r in ['id','dbid']:continue
        if dic[r]:
            #print "r:%s\n%s" % (r,dic[r])
            if dbid == 'G00D9108307' and r == 'tc':
                #print dic[r]
                #print type(dic[r])
                #print "find rn:",str(dic[r]).find('\r\n')
                #print "find n:",str(dic[r]).find('\n')
                #print "find r:",str(dic[r]).find('\r')
                pass
            if type(dic[r]) == list:
                print >> wf, "%s %s" % (r,dic[r][0])
                for tp in dic[r][1:]:
                    print >> wf," %s" % tp
            else:
                if str(dic[r]).find('\r\n') != -1 or str(dic[r]).find('\r') != -1 or str(dic[r]).find('\n') != -1:
                    print >> wf , "%s " % r
                    spstr = str(dic[r]).find('\r\n') != -1 and '\r\n' or str(dic[r]).find('\r') != -1 and '\r' or '\n'
                    for tp in dic[r].split(spstr):
                        print >>wf ," %s" % tp
                else:
                    tp = str(dic[r])
                    print >> wf , "%s %s" % (r,tp)
    print >> wf , "/"
    wf.close()
    
def set_dic(st):
    '''
    將設定檔打包成:
    dic_da[etd_main_1] = 'aue'
    dic_da[etd_main_2] = 'aue'
    .....
    '''
    dic_ta, dic_da, ta = [], {}, ''
    wf = open(st,'r')
    for l in wf.readlines():
        l = l.strip()
        if l[0] == "#": continue
        if len(l) > 0 and l.find(':') != -1:
            dic_ta.append(l[:-1])
            ta = l[:-1]
            continue
        r , num = l.split('=')
        dic_da["%s_%s"%(ta,r)] = num.strip()
    wf.close()
    return dic_ta,dic_da

def strtoutf8(tstr):
    if not tstr:
        return False
    twf = open('tt.txt','w')
    print >> twf,str(tstr)
    twf.close()
    twf = open('tt.txt','rb')
    try:
        r = twf.read().strip().decode("big5").encode("utf8")
    except:
        r = twf.read()
    twf.close()
    return r
    
def pslog(msg, msg1='',lv=0):
    wf = open('/tmp/readsql.txt', 'a')
    import time
    ptime = '%04d/%02d/%02d--%02d:%02d:%02d' % time.localtime()[0:6]
    print >> wf, '%s--%s%s:%s' % (ptime,"\t"*lv, msg, msg1)
    wf.close()
 
main()
