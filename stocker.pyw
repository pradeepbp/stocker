#!/usr/bin/python


'''
stocker.pyw
v: beta 
date: 02-04-2011 
author: pradeep balan pillai (pradeepbpin@gmail.com)

'''

import urllib2
import pickle
import gtk


class Stocker:
   
    
    def __init__(self):
        
        self.index_table = []
        self.load_tickers() 
        self.draw_gui()


    # Function to load the ticker list from a file (pickeled)
    def load_tickers(self):
        #ticker_file = open('ticker_list','wb')
        #pickle.dump(self.tickers, ticker_file)
        ticker_file = open('ticker_list', 'rb')
        if(ticker_file.readlines() == []):  # Check whether the file contains data
            ticker_file.close()             # else add data before initiating
            self.add_stock()
            ticker_file = open('ticker_list','rb')
            self.tickers = pickle.load(ticker_file)
        else:
            ticker_file = open('ticker_list','rb')
            self.tickers = pickle.load(ticker_file)
        ticker_file.close()

    # Error dialog for HTTP errors
    def error_HTTP(self):
        err = gtk.MessageDialog(self.win, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR,
                                gtk.BUTTONS_OK, 'Cannot retrieve data')
        resp = err.run()
        if resp == gtk.RESPONSE_OK:
            err.destroy()

    # Generate a request object and get the ticker data and populate ticker table
    def get_quote(self):
        index_table = []
        try:
            for key in self.tickers.keys():
                urlstring = ('http://download.finance.yahoo.com/d/quotes.csv?s='
                            + self.tickers[key]+'&f=sl1d1t1c1ohgv&e=.csv')
                data = [urllib2.urlopen(urlstring).read()]
                data_in_list = data[0].split(',')
                data_in_list[0] = key
                self.index_table.append(data_in_list)
        except:
            self.error_HTTP()

    # Calling this function will fetch fresh values for the stock ticker
    # Future implementation would be to call this function at fixed intervals resulting
    # in auto refresh
    def refresh_data(self, widget):
        self.liststore.clear()
        self.index_table = []
        self.get_quote()
        for row in self.index_table:
            per_change = round(
                    (float(row[4])/(float(row[1])-float(row[4])))*100,2)
            self.liststore.append([row[0],row[1],row[4], str(per_change)+'%'])



    # Add a new stock ticker to the display
    def add_stock(self):
        
        self.add_stock_dialog = gtk.Dialog('Add stock', self.win,
                            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                            (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                            gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
       
        self.add_stock_dialog.set_title('Add stock')
        # create the dialog components
        layout = gtk.Table(2,2)
        
        ticker_entry = gtk.Entry()
        display_name_entry = gtk.Entry()

        ticker_label = gtk.Label('Stock code:')
        name_label = gtk.Label('Display name:')

        layout.attach(ticker_label,0, 1,0,1,gtk.FILL, gtk.FILL)
        layout.attach(name_label, 0, 1, 1, 2, gtk.FILL, gtk.FILL)
        layout.attach(ticker_entry, 1,2,0,1, gtk.FILL, gtk.FILL)
        layout.attach(display_name_entry, 1, 2, 1, 2, gtk.FILL, gtk.FILL)
        self.add_stock_dialog.vbox.pack_start(layout, True, True, 0)

        self.add_stock_dialog.show_all()
        resp = self.add_stock_dialog.run()
        
        if resp == gtk.RESPONSE_ACCEPT:
            add_stock_list = []
            add_stock_list.append(display_name_entry.get_text())
            add_stock_list.append(ticker_entry.get_text())
            print add_stock_list

            # load the tickers from file and then append to the dicionary
            ticker_file = open('ticker_list', 'rb')
            self.tickers = pickle.load(ticker_file)
            ticker_file.close()

            # after appending write the new dictionary to the file
            ticker_file = open('ticker_list', 'wb')
            self.tickers[add_stock_list[0]] = add_stock_list[1]
            pickle.dump(self.tickers, ticker_file)
            ticker_file.close()

            self.add_stock_dialog.destroy()
            
        elif resp == gtk.RESPONSE_REJECT:
            self.add_stock_dialog.destroy()



    # Delete an existing ticker from the display
    def delete_stock(self):
        # Create the main dialog box
        self.delete_stock_dialog = gtk.Dialog('Delete stock', self.win,
                                    gtk.DIALOG_MODAL,
                                    (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                                     'Delete', gtk.RESPONSE_ACCEPT))
        self.delete_stock_dialog.set_title('Delete stock')
        # dialog widget components
        # Get data from file to populate the combo box
        fhandler = open('ticker_list','rb')
        self.tickers = pickle.load(fhandler)
        fhandler.close()

        cbox = gtk.combo_box_new_text()
        for key in self.tickers.keys():
            cbox.append_text(key)
        self.delete_stock_dialog.vbox.pack_start(cbox)
        self.delete_stock_dialog.show_all()

        resp = self.delete_stock_dialog.run()

        if resp == gtk.RESPONSE_ACCEPT:
            del_stock = cbox.get_active_text()

            # Rewrite the date file excluding the deleted stock
            # Also, ensure that atlease one entry remains in the date file
            if del_stock != 'BSE':
                del self.tickers[del_stock]
                fhandler = open('ticker_list','wb')
                pickle.dump(self.tickers, fhandler)
                fhandler.close()
                self.delete_stock_dialog.destroy()
            else:
                self.delete_stock_dialog.destroy() 
                warning = gtk.MessageDialog(self.win, gtk.DIALOG_MODAL,
                                    gtk.MESSAGE_WARNING, gtk.BUTTONS_OK,
                                    'Cannot delete that item')
                resp = warning.run()
                if resp == gtk.RESPONSE_OK:
                    warning.destroy()
        # if user cancels the operation, close the dialog
        elif resp == gtk.RESPONSE_REJECT:
            self.delete_stock_dialog.destroy()

    # Returns False if the ticker List file is empty, else return True
    def get_ticker_list_status(self):
        tick_file = open('ticker_list','rb')
        if tick_file.readlines() == Null:
            tick_file.close()
            return False
        else:
            tick_file.close()
            return True


    # Displays the list of stocks watches along with stock code
    def display_watchlist(self):

        display_string = ""
        for key in self.tickers.keys():
            display_string = (display_string + key +' [' + self.tickers[key] +
                                ']\n')

        watchlist_display = gtk.MessageDialog(self.win, gtk.DIALOG_MODAL,
                            gtk.MESSAGE_INFO, gtk.BUTTONS_OK,
                            display_string)
        watchlist_display.set_title('Watchlist')
        resp = watchlist_display.run()
        if resp == gtk.RESPONSE_OK:
            watchlist_display.destroy()

    # Display help file
    def show_help(self):
        help_string = ""
        fhelp = open('help.txt', 'r')
        help_info = fhelp.readlines()
        fhelp.close()
        
        for line in help_info:
            help_string = help_string + line
        
        help_dialog = gtk.MessageDialog(self.win, gtk.DIALOG_MODAL,
                            gtk.MESSAGE_INFO, gtk.BUTTONS_OK,
                            help_string)
        help_dialog.set_title('Help')
        resp = help_dialog.run()
        if resp == gtk.RESPONSE_OK:
            help_dialog.destroy()

    # About dialog display
    def about_dialog(self):
        about = gtk.AboutDialog()
        about.set_name('STOCKER')
        about.set_version('Beta')
        about.set_icon(None)
        resp = about.run()
        if resp == gtk.RESPONSE_CANCEL:
            about.destroy()

    # This function draws the GUI and initialises the GUI elements
    def draw_gui(self):
        #basic widgets
        self.win = gtk.Window()
        self.win.set_default_size(400,300)
        self.win.set_title('STOCKER')
        self.win.set_icon_from_file('Stocker-icon.png')
        layout = gtk.Table(3,1,False)
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        refresh_button = gtk.Button("_Refresh", use_underline = True)
        refresh_button.set_sensitive(True)    

        # Create the menu items
        menu_bar = gtk.MenuBar()

        file_menu_item = gtk.MenuItem('_File', True)
        help_menu_item = gtk.MenuItem('_Help', True)
        view_menu_item = gtk.MenuItem('_View', True)

        file_menu = gtk.Menu()
        help_menu = gtk.Menu()
        view_menu = gtk.Menu()


        file_menu_item.set_submenu(file_menu)
        view_menu_item.set_submenu(view_menu)
        help_menu_item.set_submenu(help_menu)
        

        file_menu_item_add = gtk.MenuItem('_Add stock...', True)
        file_menu_item_delete = gtk.MenuItem('_Delete stock...', True)
        file_menu_item_delete.set_sensitive(True)
        file_menu_item_exit = gtk.MenuItem('E_xit', True)

        view_menu_item_watchlist = gtk.MenuItem('_Watchlist', True)

        help_menu_item_help = gtk.MenuItem('_Help', True)
        help_menu_item_about = gtk.MenuItem('_About', True)

        file_menu.append(file_menu_item_add)
        file_menu.append(file_menu_item_delete)
        file_menu.append(file_menu_item_exit)

        view_menu.append(view_menu_item_watchlist)

        help_menu.append(help_menu_item_help)
        help_menu.append(help_menu_item_about)

        menu_bar.append(file_menu_item)
        menu_bar.append(view_menu_item)
        menu_bar.append(help_menu_item)


        # Add menu item signals
        file_menu_item_add.connect('activate',
                                    lambda a: self.add_stock())
        file_menu_item_delete.connect('activate',
                                    lambda a: self.delete_stock())
        file_menu_item_exit.connect('activate', lambda q: gtk.main_quit())

        view_menu_item_watchlist.connect('activate',
                                        lambda a: self.display_watchlist())
        help_menu_item_help.connect('activate', lambda h: self.show_help())
        help_menu_item_about.connect('activate',
                                    lambda a: self.about_dialog())



        # Get quote for the first display
        self.get_quote()

        
        #the display table
        self.liststore = gtk.ListStore(str,str,str,str)

        for row in self.index_table:
            per_change = round(
                    (float(row[4])/(float(row[1])-float(row[4])))*100,2)
            self.liststore.append([row[0],row[1],row[4], str(per_change)+'%'])

        treeview = gtk.TreeView(self.liststore)
        column_stock = gtk.TreeViewColumn('Stock')
        column_price = gtk.TreeViewColumn('Price')
        column_change = gtk.TreeViewColumn('Change')
        column_perchange = gtk.TreeViewColumn('% Change')
        treeview.append_column(column_stock)
        treeview.append_column(column_price)
        treeview.append_column(column_change)
        treeview.append_column(column_perchange)

        cellrenderer_stock = gtk.CellRendererText()
        cellrenderer_price = gtk.CellRendererText()
        cellrenderer_change = gtk.CellRendererText()
        cellrenderer_perchange = gtk.CellRendererText()
        
        column_stock.pack_start(cellrenderer_stock)
        column_stock.add_attribute(cellrenderer_stock, 'text', 0)
        column_price.pack_start(cellrenderer_price)
        column_price.add_attribute(cellrenderer_price, 'text', 1)
        column_change.pack_start(cellrenderer_change)
        column_change.add_attribute(cellrenderer_change, 'text', 2)
        column_perchange.pack_start(cellrenderer_perchange)
        column_perchange.add_attribute(cellrenderer_perchange, 'text', 3)


        layout.attach(menu_bar, 0,1,0,1, gtk.EXPAND|gtk.FILL, gtk.FILL)
        layout.attach(scroll, 0,1,1,2)
        layout.attach(refresh_button, 0,1,2,3, gtk.SHRINK, gtk.SHRINK)

        scroll.add(treeview)
        self.win.add(layout)
        refresh_button.connect('clicked', self.refresh_data)
        self.win.connect('destroy', lambda q: gtk.main_quit())
        self.win.show_all()


if __name__ == "__main__":
    Stocker()
    gtk.main()



