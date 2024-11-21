/*
 * Copyright (c) 2019, Seqera Labs.
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 *
 * This Source Code Form is "Incompatible With Secondary Licenses", as
 * defined by the Mozilla Public License, v. 2.0.
 */

package io.seqera.mail

import groovy.text.GStringTemplateEngine
import groovy.transform.CompileStatic

/**
 * Helper functions to handle mail notification
 *
 * @author Paolo Di Tommaso <paolo.ditommaso@gmail.com>
 */
@CompileStatic
class MailHelper {

    static String getTemplateFile(String classpathResource, Map binding) {

        // Log the effective classpath
        System.out.println("Effective classpath: " + System.getProperty("java.class.path"));

        // Log the classpath root
        URL root = Thread.currentThread().getContextClassLoader().getResource("");
        System.out.println("Classpath root: " + (root != null ? root.toString() : "null"));

        // Attempt to locate the resource
        URL resource = Thread.currentThread().getContextClassLoader().getResource(classpathResource);
        System.out.println("Resource URL: " + (resource != null ? resource.toString() : "not found"));

        // Load the resource stream
        def source = Thread.currentThread().getContextClassLoader().getResourceAsStream(classpathResource);
        System.out.println("Stream URL: " + (source != null ? "Stream is loaded successfully" : "Stream not found"));

        // If the resource stream is null, throw an error
        if (!source) {
            throw new IllegalArgumentException("Cannot load notification default template -- check classpath resource: " + classpathResource);
        }

        // Process the template and return the result
        return loadMailTemplate0(source, binding);
    }

    static private String loadMailTemplate0(InputStream source, Map binding) {
        // Copy the binding into a new map
        def map = new HashMap();
        map.putAll(binding);

        System.out.println("Binding variables: " + map);

        // Process the template using GStringTemplateEngine
        def template = new GStringTemplateEngine().createTemplate(new InputStreamReader(source));
        return template.make(map).toString();
    }
}
