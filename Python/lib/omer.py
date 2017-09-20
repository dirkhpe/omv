"""
This module consolidates all communication with the OMER MS Access database.
"""
import logging
import os
import pypyodbc
import sys
from collections import namedtuple


class Datastore:

    def __init__(self, config):

        dbpath = config['OmerDB']['dbpath']
        dbfile = config['OmerDB']['dbfile']
        dbloc = os.path.join(dbpath, dbfile)
        conn_str = 'driver=Microsoft Access Driver (*.mdb, *.accdb);dbq={l}'.format(l=dbloc)
        logging.info("Connection String: %s", conn_str)
        try:
            self.cnx = pypyodbc.connect(conn_str)
        except pypyodbc.Error:
            e = sys.exc_info()[1]
            ec = sys.exc_info()[0]
            logmsg = "Error Class: %s, Message: %s"
            logging.critical(logmsg, ec, e)
            sys.exit()
        logmsg = "Connection Successful"
        logging.debug(logmsg)
        self.cursor = self.cnx.cursor()

    def close_conn(self):
        self.cnx.close()
        return True

    def get_named_row(self, nt_name):
        """
        This method will create a named tuple row for the current cursor.

        :param nt_name: Named Tuple name. (not sure when this is used?)

        :return: namedtuple class with name "named_row"
        """
        # Get column names
        field_list = [x[0] for x in self.cursor.description]
        # Create named tuple subclass with name "named_row"
        named_row = namedtuple(nt_name, field_list, rename=True)
        return named_row

    def get_table(self, tablename):
        """
        This method will return the table as a list of named rows. This means that each row in the list will return
        the table column value as an attribute. E.g. row.name will return the value for column name in each row.
        @param tablename:
        @return:
        """
        query = "SELECT * FROM {t}".format(t=tablename)
        self.cursor.execute(query)
        named_row = self.get_named_row(tablename)
        rec_list = [row for row in map(named_row._make, self.cursor.fetchall())]
        return rec_list

    def res_query(self, query, qname):
        self.cursor.execute(query)
        named_row = self.get_named_row(qname)
        rec_list = [row for row in map(named_row._make, self.cursor.fetchall())]
        return rec_list

    def samenstellen_han_vwp(self):
        """
        This method will collect the info for path 'Samenstellen Dossier - HandelingVoorwerp' (Green line).
        :return:
        """
        query = """
        SELECT distinct pt.proj_code as uptype_code, pt.proj_naamlang as uptype_naam,
                        tds.stuk_naam as updocument_naam, tds.stuk_code as updocument_code
        FROM (((((((tp_projecttype pt)
        INNER JOIN tp_projectfase AS pf ON pf.prof_fk_proj_id = pt.proj_id)
        INNER JOIN tp_dossiertype AS dt ON dt.dost_fk_projfase_id = pf.prof_id)
        INNER JOIN tp_dossierinhouddef AS did ON did.dosinh_id = dt.dost_fk_dosinh_id)
        INNER JOIN tabxx_dos_hanvwp AS tdh ON tdh.xdhv_fk_dosinh_id = did.dosinh_id)
        INNER JOIN tabx_han_vwp AS thv ON thv.xhv_key = tdh.xdhv_fk_xhv)
        INNER JOIN tabx_stuk_all AS tsa ON tsa.xdsta_fk_hanvwp = thv.xhv_key)
        INNER JOIN tabdossierstuk AS tds ON tsa.xdsta_fk_stuk = tds.stuk_key
        """
        return self.res_query(query, 'samenstellen_han_vwp')

    def samenstellen_han_vwp_functie(self):
        query = """
        SELECT distinct pt.proj_code as uptype_code, pt.proj_naamlang as uptype_naam,
                        tdb.blok_blokid as updocument_code, tdb.blok_naam as updocument_naam
        FROM ((((((((tp_projecttype pt)
        INNER JOIN tp_projectfase AS pf ON pf.prof_fk_proj_id = pt.proj_id)
        INNER JOIN tp_dossiertype AS dt ON dt.dost_fk_projfase_id = pf.prof_id)
        INNER JOIN tp_dossierinhouddef AS did ON did.dosinh_id = dt.dost_fk_dosinh_id)
        INNER JOIN tabxx_dos_hanvwp AS tdh ON tdh.xdhv_fk_dosinh_id = did.dosinh_id)
        INNER JOIN tabx_han_vwp AS thv ON thv.xhv_key = tdh.xdhv_fk_xhv)
        INNER JOIN tabx_hanvwp_fun AS thvf ON thvf.xhvf_fk_xhv = thv.xhv_key)
        INNER JOIN tabxx_hvf_blk AS tb ON thvf.xhvf_key = tb.xhvfb_fk_xhvf)
        INNER JOIN tabdatablok AS tdb ON tb.xhvfb_fk_datablok = tdb.blok_key
        """
        return self.res_query(query, 'samenstellen_han_vwp_functie')

    def samenstellen_han_vwp_fun_full(self):
        query = """
        SELECT distinct pt.proj_code as uptype_code, pt.proj_naamlang as uptype_naam,
                        v.parvwp_naam as voorwerp, h.parhan_naam as handeling, f.parfun_naam as functie,
                        tdb.blok_blokid as updocument_code, tdb.blok_naam as updocument_naam
        FROM (((((((((((tp_projecttype pt)
        LEFT JOIN tp_projectfase AS pf ON pf.prof_fk_proj_id = pt.proj_id)
        LEFT JOIN tp_dossiertype AS dt ON dt.dost_fk_projfase_id = pf.prof_id)
        LEFT JOIN tp_dossierinhouddef AS did ON did.dosinh_id = dt.dost_fk_dosinh_id)
        LEFT JOIN tabxx_dos_hanvwp AS tdh ON tdh.xdhv_fk_dosinh_id = did.dosinh_id)
        LEFT JOIN tabx_han_vwp AS thv ON thv.xhv_key = tdh.xdhv_fk_xhv)
        LEFT JOIN tabpara_voorwerp AS v ON v.parvwp_key = thv.xhv_fk_parvwp)
        LEFT JOIN tabpara_handeling AS h ON h.parhan_key = thv.xhv_fk_parhan)
        LEFT JOIN tabx_hanvwp_fun AS thvf ON thvf.xhvf_fk_xhv = thv.xhv_key)
        LEFT JOIN tabpara_functie AS f ON f.parfun_key = thvf.xhvf_fk_parfun)
        LEFT JOIN tabxx_hvf_blk AS tb ON thvf.xhvf_key = tb.xhvfb_fk_xhvf)
        LEFT JOIN tabdatablok AS tdb ON tb.xhvfb_fk_datablok = tdb.blok_key
        """
        return self.res_query(query, 'samenstellen_han_vwp_fun_full')

    def samenstellen_vast(self):
        query = """
        SELECT distinct pt.proj_code as uptype_code, pt.proj_naamlang as uptype_naam,
               ds.stuk_code as updocument_code, ds.stuk_naam as updocument_naam
        FROM ((tp_projecttype AS pt)
        INNER JOIN tpx_proj_stuk AS ps ON ps.xprst_fk_proj_id = pt.proj_id)
        INNER JOIN tabdossierstuk AS ds ON ds.stuk_key = ps.xprst_fk_stuk_key
        """
        return self.res_query(query, 'samenstellen_vast')

    def x_samenstellen_milieu(self):
        """
        De query via DossierInhoudDef naar DossierType geeft teveel Dossierstukken terug. Gebruik NIET deze query, maar
        gebruik query samenstellen_milieu_projecttype ipv deze query.
        :return:
        """
        query = """
        SELECT distinct pt.proj_code as uptype_code, pt.proj_naamlang as uptype_naam,
                        ds.stuk_naam as updocument_naam, ds.stuk_code as updocument_code
        FROM (((((((((((tp_projecttype pt)
        INNER JOIN tp_projectfase AS pf ON pf.prof_fk_proj_id = pt.proj_id)
        INNER JOIN tp_dossiertype AS dt ON dt.dost_fk_projfase_id = pf.prof_id)
        INNER JOIN tp_dossierinhouddef AS did ON did.dosinh_id = dt.dost_fk_dosinh_id)
        INNER JOIN oglx_doss_vwp_dond AS dvd ON did.dosinh_id=dvd.xdvd_fk_dosinh_id)
        INNER JOIN ogl_dossieronderdeeltype AS dot ON dvd.xdvd_dond_id=dot.dond_id)
        INNER JOIN oglx_dossdeel_formdeel AS df ON dot.dond_id = df.xdofo_dond_id)
        INNER JOIN ogl_formulieronderdeeltype AS fotp
                                             ON df.xdofo_fond_id=fotp.fond_id)
        INNER JOIN ogl_formdeel_form AS ff ON fotp.fond_id = ff.fonf_fond_parentid)
        INNER JOIN ogl_formulieronderdeeltype AS fotc
                                           ON ff.fonf_fond_childid = fotc.fond_id)
        INNER JOIN ogl_formdeel_stuk AS fs ON fotc.fond_id = fs.fons_fond_id)
        INNER JOIN tabdossierstuk AS ds ON fs.fons_stuk_id = ds.stuk_key
        """
        return self.res_query(query, 'samenstellen_vast')

    def samenstellen_milieu_projecttype(self):
        """
        Zie beschrijving bij functie x_samenstellen_milieu.
        :return:
        """
        query = """
        SELECT distinct pt.proj_code as uptype_code, pt.proj_naamlang as uptype_naam,
               ds.stuk_code as updocument_code, ds.stuk_naam as updocument_naam
        FROM ((((tp_projecttype pt)
        INNER JOIN tpx_formdeel_projtype AS fpt ON fpt.xfdpt_fk_proj_id=pt.proj_id)
        INNER JOIN ogl_formulieronderdeeltype AS fot ON fot.fond_id = fpt.xfdpt_fk_fond_id)
        INNER JOIN ogl_formdeel_stuk AS fs ON fs.fons_fond_id = fot.fond_id)
        INNER JOIN tabdossierstuk AS ds ON ds.stuk_key = fs.fons_stuk_id;
        """
        return self.res_query(query, 'samenstellen_milieu_projecttype')

    def samenstellen_milieu_stuk_blok(self):
        """
        Aanpassing van functie samenstellen_milieu_projecttype. Een dossierstuk kan mogelijks ook nog een datablok
        hebben. Beide moeten opgeslagen kunnen worden.
        :return:
        """
        query = """
        SELECT distinct pt.proj_code as uptype_code, pt.proj_naamlang as uptype_naam,
               ds.stuk_code as updocument_code, ds.stuk_naam as updocument_naam,
               sb.xdsb_key, db.blok_blokid, db.blok_naam
        FROM ((((((tp_projecttype pt)
        INNER JOIN tpx_formdeel_projtype AS fpt ON fpt.xfdpt_fk_proj_id=pt.proj_id)
        INNER JOIN ogl_formulieronderdeeltype AS fot ON fot.fond_id = fpt.xfdpt_fk_fond_id)
        INNER JOIN ogl_formdeel_stuk AS fs ON fs.fons_fond_id = fot.fond_id)
        INNER JOIN tabdossierstuk AS ds ON ds.stuk_key = fs.fons_stuk_id)
        LEFT JOIN tabx_stuk_blk AS sb ON sb.xdsb_fk_stuk = ds.stuk_key)
        LEFT JOIN tabdatablok AS db ON db.blok_key = sb.xdsb_fk_blok;
        """
        return self.res_query(query, 'samenstellen_milieu_projecttype')

    def proces_type_docs(self):
        """
        Bereken documenten voor processing. Start van Project type ipv Dossierstatus.
        :return:
        """
        query = """
        SELECT distinct pt.proj_code as uptype_code, pt.proj_naamlang as uptype_naam,
                        df.dosf_code as upfase_code, df.dosf_naam as upfase_naam,
                        g.geb_code as upgebeurtenis_code, g.geb_naam as upgebeurtenis_naam,
                        iif(ds.stuk_code is null, b.blok_blokid, ds.stuk_code) as updocument_code,
                        iif(ds.stuk_code is null, b.blok_naam, ds.stuk_naam) as updocument_naam,
                        iif(ds.stuk_code is null, 'datablok', 'dossierstuk') as doc_type
        FROM (((((((((((((tp_projecttype pt)
        LEFT JOIN tp_projectfase AS pf ON pf.prof_fk_proj_id = pt.proj_id)
        LEFT JOIN tabfase AS f ON f.fase_id = pf.prof_fk_fase_id)
        LEFT JOIN tp_dossiertype AS dt ON dt.dost_fk_projfase_id = pf.prof_id)
        LEFT JOIN tp_procesdef AS pd ON pd.proc_id = dt.dost_fk_proc_id)
        LEFT JOIN tabdossierfase AS df ON df.dosf_fk_proc_id = pd.proc_id)
        LEFT JOIN tabdossierstatus AS dstat ON dstat.stat_fk_dosf = df.dosf_key)
        LEFT JOIN tabx_stat_gebuse AS sgu on dstat.stat_key = sgu.xsgu_fk_stat)
        LEFT JOIN tabxx_gebuse AS gu on sgu.xsgu_fk_gebuse = gu.gebu_key)
        LEFT JOIN tabgebeurtenis AS g on gu.gebu_fk_gebeurt = g.geb_key)
        LEFT JOIN tabx_stuk_all AS sa on g.geb_key = sa.xdsta_fk_gebeurt)
        LEFT JOIN tabdossierstuk AS ds on sa.xdsta_fk_stuk = ds.stuk_key)
        LEFT JOIN tabx_geb_blk AS gb on g.geb_key = gb.xgb_fk_gebeurt)
        LEFT JOIN tabdatablok AS b on gb.xgb_fk_blok = b.blok_key
        WHERE NOT ((b.blok_code is null) AND (ds.stuk_code is null));
        """
        return self.res_query(query, 'proces_type_docs')

    def process_type_docs_blok(self):
        """
        Bereken documenten voor processing. Start van Project ipv Dossierstatus.
        Er kan een dossierstuk en een datablok gevonden worden. Datablokken moeten gezocht worden via
        tabx_geb_blk en via tabx_stuk_blk.
        :return:
        """
        query = """
        SELECT distinct pt.proj_code as uptype_code, pt.proj_naamlang as uptype_naam,
                        df.dosf_code as upfase_code, df.dosf_naam as upfase_naam,
                        g.geb_code as upgebeurtenis_code, g.geb_naam as upgebeurtenis_naam,
                        ds.stuk_naam as updocument_naam, ds.stuk_code as updocument_code,
                        db.blok_naam as db_blok_naam, db.blok_blokid as db_blok_code,
                        b.blok_naam as b_blok_naam, b.blok_blokid as b_blok_code
        FROM (((((((((((((((tp_projecttype pt)
        LEFT JOIN tp_projectfase AS pf ON pf.prof_fk_proj_id = pt.proj_id)
        LEFT JOIN tabfase AS f ON f.fase_id = pf.prof_fk_fase_id)
        LEFT JOIN tp_dossiertype AS dt ON dt.dost_fk_projfase_id = pf.prof_id)
        LEFT JOIN tp_procesdef AS pd ON pd.proc_id = dt.dost_fk_proc_id)
        LEFT JOIN tabdossierfase AS df ON df.dosf_fk_proc_id = pd.proc_id)
        LEFT JOIN tabdossierstatus AS dstat ON dstat.stat_fk_dosf = df.dosf_key)
        LEFT JOIN tabx_stat_gebuse AS sgu on dstat.stat_key = sgu.xsgu_fk_stat)
        LEFT JOIN tabxx_gebuse AS gu on sgu.xsgu_fk_gebuse = gu.gebu_key)
        LEFT JOIN tabgebeurtenis AS g on gu.gebu_fk_gebeurt = g.geb_key)
        LEFT JOIN tabx_stuk_all AS sa on g.geb_key = sa.xdsta_fk_gebeurt)
        LEFT JOIN tabdossierstuk AS ds on sa.xdsta_fk_stuk = ds.stuk_key)
        LEFT JOIN tabx_stuk_blk AS sb on sb.xdsb_fk_stuk = ds.stuk_key)
        LEFT JOIN tabdatablok AS db on db.blok_key = sb.xdsb_fk_blok)
        LEFT JOIN tabx_geb_blk AS gb on g.geb_key = gb.xgb_fk_gebeurt)
        LEFT JOIN tabdatablok AS b on gb.xgb_fk_blok = b.blok_key
        WHERE NOT ((b.blok_code is null) AND (ds.stuk_code is null));
        """
        return  self.res_query(query, 'process_type_docs_blok')

    def samenstellen_formdeel_vast(self):
        """
        Dit is het proces deel van Formdeel vast - maar het is nog niet duidelijk wat hiermee bedoeld wordt.
        :return:
        """
        query = """
        SELECT distinct pt.proj_code as uptype_code, pt.proj_naamlang as uptype_naam,
                        fot.fond_code, fdv.fonv_fond_id, fdvt.fonvt_code
        FROM ((((tp_projecttype pt)
        INNER JOIN tpx_formdeel_projtype AS fpt ON fpt.xfdpt_fk_proj_id=pt.proj_id)
        INNER JOIN ogl_formulieronderdeeltype AS fot ON fot.fond_id = fpt.xfdpt_fk_fond_id)
        INNER JOIN ogl_formdeel_vast AS fdv ON fdv.fonv_fond_id = fot.fond_id)
        INNER JOIN ogl_formdeel_vasttype AS fdvt ON fdvt.fonvt_id = fdv.fonv_vasttype_id
        """
        return  self.res_query(query, 'samenstellen_formdeel_vast')
