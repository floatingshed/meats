/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package com.googlecode.meats;

import org.netbeans.microedition.lcdui.SimpleTableModel;

/**
 * This is a table model of common MIDP java.lang.System
 * properties.
 *
 * @author olaija
 */
public class PropertiesTableModel extends SimpleTableModel {

    public PropertiesTableModel() {
        super(new String[][]{
                    // too long:
                    // new String[]{"30", "microedition.platform", "null"},
                    new String[]{"30", "microedition.configuration", "CLDC-1.0"},
                    new String[]{"30", "microedition.profiles", "null"},
                    new String[]{"37", "microedition.locale", "null"},
                    new String[]{"30", "microedition.encoding", "ISO8859_1"},
                    // repeated
                    // new String[]{"37", "microedition.profiles", "MIDP-1.0"},
                    new String[]{"75", "microedition.io.file.FileConnection.version", "1.0"},
                    new String[]{"75", "file.separator", "(impl-dep)"},
                    new String[]{"75", "microedition.pim.version", "1.0"},
                    // repeated
                    // new String[]{"118", "microedition.locale", "null"},
                    // repeated
                    // new String[]{"118", "microedition.profiles", "MIDP-2.0"},
                    new String[]{"118", "microedition.commports", "(impl-dep)"},
                    new String[]{"118", "microedition.hostname", "(impl-dep)"},
                    // repeated in 205
                    // new String[]{"120", "wireless.messaging.sms.smsc", "(impl-dep)"},
                    // repeated, too long:
                    // new String[]{"139", "microedition.platform", "(impl-dep)"},
                    // repeated
                    // new String[]{"139", "microedition.encoding", "ISO8859-1"},
                    // repeated
                    // new String[]{"139", "microedition.configuration", "CLDC-1.1"},
                    // repeated
                    // new String[]{"139", "microedition.profiles", "(impl-dep)"},
                    new String[]{"177", "microedition.smartcardslots", "(impl-dep)"},
                    new String[]{"179", "microedition.location.version", "1.0"},
                    new String[]{"180", "microedition.sip.version", "1.0"},
                    new String[]{"184", "microedition.m3g.version", "1.0"},
                    new String[]{"185", "microedition.jtwi.version", "1.0"},
                    // repeated
                    // new String[]{"195", "microedition.locale", "(impl-dep)"},
                    // repeated
                    // new String[]{"195", "microedition.profiles", "IMP-1.0"},
                    new String[]{"205", "wireless.messaging.sms.smsc", "(impl-dep)"},
                    // long value; and I don't use MMS ;)
                    // new String[]{"205", "wireless.messaging.mms.mmsc", "(impl-dep)"},
                    new String[]{"211", "CHAPI-Version", "1.0"}
                },
                // exchanged value with JSR
                new String[]{"Value", "Property", "JSR"});
    }

    public Object getValue(int col, int row) {
        // exchanged value with JSR
        col = 2 - col;
        if ( col == 2 )
            return System.getProperty((String)super.getValue(1, row));
        else if ( col == 1 ) {
            String val = (String)super.getValue(col, row);
            return val.length() < 30 ? val : val.substring(0, 27).concat("...");
        }

        return super.getValue(col, row);
    }
}
