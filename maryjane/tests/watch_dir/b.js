
/*!
    joop: javascript OOP toolkit
    author: Vahid Mardani
    version: 1.3
*/

/*!
 * sprintf.js
 * Copyright (c) 2007-2013 Alexandru Marasteanu <hello at alexei dot ro>
 * 3 clause BSD license
 * */

(function(ctx) {
	var sprintf = function() {
		if (!sprintf.cache.hasOwnProperty(arguments[0])) {
			sprintf.cache[arguments[0]] = sprintf.parse(arguments[0]);
		}
		return sprintf.format.call(null, sprintf.cache[arguments[0]], arguments);
	};

	sprintf.format = function(parse_tree, argv) {
		var cursor = 1, tree_length = parse_tree.length, node_type = '', arg, output = [], i, k, match, pad, pad_character, pad_length;
		for (i = 0; i < tree_length; i++) {
			node_type = get_type(parse_tree[i]);
			if (node_type === 'string') {
				output.push(parse_tree[i]);
			}
			else if (node_type === 'array') {
				match = parse_tree[i]; // convenience purposes only
				if (match[2]) { // keyword argument
					arg = argv[cursor];
					for (k = 0; k < match[2].length; k++) {
						if (!arg.hasOwnProperty(match[2][k])) {
							throw(sprintf('[sprintf] property "%s" does not exist', match[2][k]));
						}
						arg = arg[match[2][k]];
					}
				}
				else if (match[1]) { // positional argument (explicit)
					arg = argv[match[1]];
				}
				else { // positional argument (implicit)
					arg = argv[cursor++];
				}

				if (/[^s]/.test(match[8]) && (get_type(arg) != 'number')) {
					throw(sprintf('[sprintf] expecting number but found %s', get_type(arg)));
				}
				switch (match[8]) {
					case 'b': arg = arg.toString(2); break;
					case 'c': arg = String.fromCharCode(arg); break;
					case 'd': arg = parseInt(arg, 10); break;
					case 'e': arg = match[7] ? arg.toExponential(match[7]) : arg.toExponential(); break;
					case 'f': arg = match[7] ? parseFloat(arg).toFixed(match[7]) : parseFloat(arg); break;
					case 'o': arg = arg.toString(8); break;
					case 's': arg = ((arg = String(arg)) && match[7] ? arg.substring(0, match[7]) : arg); break;
					case 'u': arg = arg >>> 0; break;
					case 'x': arg = arg.toString(16); break;
					case 'X': arg = arg.toString(16).toUpperCase(); break;
				}
				arg = (/[def]/.test(match[8]) && match[3] && arg >= 0 ? '+'+ arg : arg);
				pad_character = match[4] ? match[4] == '0' ? '0' : match[4].charAt(1) : ' ';
				pad_length = match[6] - String(arg).length;
				pad = match[6] ? str_repeat(pad_character, pad_length) : '';
				output.push(match[5] ? arg + pad : pad + arg);
			}
		}
		return output.join('');
	};

	sprintf.cache = {};

	sprintf.parse = function(fmt) {
		var _fmt = fmt, match = [], parse_tree = [], arg_names = 0;
		while (_fmt) {
			if ((match = /^[^\x25]+/.exec(_fmt)) !== null) {
				parse_tree.push(match[0]);
			}
			else if ((match = /^\x25{2}/.exec(_fmt)) !== null) {
				parse_tree.push('%');
			}
			else if ((match = /^\x25(?:([1-9]\d*)\$|\(([^\)]+)\))?(\+)?(0|'[^$])?(-)?(\d+)?(?:\.(\d+))?([b-fosuxX])/.exec(_fmt)) !== null) {
				if (match[2]) {
					arg_names |= 1;
					var field_list = [], replacement_field = match[2], field_match = [];
					if ((field_match = /^([a-z_][a-z_\d]*)/i.exec(replacement_field)) !== null) {
						field_list.push(field_match[1]);
						while ((replacement_field = replacement_field.substring(field_match[0].length)) !== '') {
							if ((field_match = /^\.([a-z_][a-z_\d]*)/i.exec(replacement_field)) !== null) {
								field_list.push(field_match[1]);
							}
							else if ((field_match = /^\[(\d+)\]/.exec(replacement_field)) !== null) {
								field_list.push(field_match[1]);
							}
							else {
								throw('[sprintf] huh?');
							}
						}
					}
					else {
						throw('[sprintf] huh?');
					}
					match[2] = field_list;
				}
				else {
					arg_names |= 2;
				}
				if (arg_names === 3) {
					throw('[sprintf] mixing positional and named placeholders is not (yet) supported');
				}
				parse_tree.push(match);
			}
			else {
				throw('[sprintf] huh?');
			}
			_fmt = _fmt.substring(match[0].length);
		}
		return parse_tree;
	};

	var vsprintf = function(fmt, argv, _argv) {
		_argv = argv.slice(0);
		_argv.splice(0, 0, fmt);
		return sprintf.apply(null, _argv);
	};

	/**
	 * helpers
	 */
	function get_type(variable) {
		return Object.prototype.toString.call(variable).slice(8, -1).toLowerCase();
	}

	function str_repeat(input, multiplier) {
		for (var output = []; multiplier > 0; output[--multiplier] = input) {/* do nothing */}
		return output.join('');
	}

	/**
	 * export to either browser or node.js
	 */
	ctx.sprintf = sprintf;
	ctx.vsprintf = vsprintf;
})(typeof exports != "undefined" ? exports : window);


// Add ECMA262-5 method binding if not supported natively
//
if (!Function.prototype.hasOwnProperty('bind')) {
    Function.prototype.bind = function (owner) {
        var that = this,
            args = Array.prototype.slice.call(arguments, 1);
        if (arguments.length <= 1) {
            return function () {
                return that.apply(owner, arguments);
            };
        }
        return function () {
            return that.apply(owner, arguments.length === 0 ? args : args.concat(Array.prototype.slice.call(arguments)));
        };

    };
}

// Add ECMA262-5 string trim if not supported natively
//
if (!String.prototype.hasOwnProperty('trim')) {
    String.prototype.trim = function () {
        return this.replace(/^\s+/, '').replace(/\s+$/, '');
    };
}

// Add ECMA262-5 Array methods if not supported natively
//
if (!Array.prototype.hasOwnProperty('indexOf')) {
    Array.prototype.indexOf = function (find, i) {
        var n;
        /*i is optional*/
        if (i === undefined) { i = 0; }
        if (i < 0) { i += this.length; }
        if (i < 0) { i = 0; }
        for (n = this.length; i < n; i += 1) {
            if (this.hasOwnProperty(i) && this[i] === find) {
                return i;
            }
        }
        return -1;
    };
}
if (!Array.prototype.hasOwnProperty('lastIndexOf')) {
    Array.prototype.lastIndexOf = function (find, i) {
        /*i is opt*/
        if (i === undefined) { i = this.length - 1; }
        if (i < 0) { i += this.length; }
        if (i > this.length - 1) { i = this.length - 1; }
        for (i++; i-->0;) /* i++ because from-argument is sadly inclusive */
            if (i in this && this[i]===find)
                return i;
        return -1;
    };
}
if (!('forEach' in Array.prototype)) {
    Array.prototype.forEach= function(action, that /*opt*/) {
        for (var i= 0, n= this.length; i<n; i++)
            if (i in this)
                action.call(that, this[i], i, this);
    };
}
if (!('map' in Array.prototype)) {
    Array.prototype.map= function(mapper, that /*opt*/) {
        var other= new Array(this.length);
        for (var i= 0, n= this.length; i<n; i++)
            if (i in this)
                other[i]= mapper.call(that, this[i], i, this);
        return other;
    };
}
if (!('filter' in Array.prototype)) {
    Array.prototype.filter= function(filter, that /*opt*/) {
        var other= [], v;
        for (var i=0, n= this.length; i<n; i++)
            if (i in this && filter.call(that, v= this[i], i, this))
                other.push(v);
        return other;
    };
}
if (!('every' in Array.prototype)) {
    Array.prototype.every= function(tester, that /*opt*/) {
        for (var i= 0, n= this.length; i<n; i++)
            if (i in this && !tester.call(that, this[i], i, this))
                return false;
        return true;
    };
}
if (!('some' in Array.prototype)) {
    Array.prototype.some= function(tester, that /*opt*/) {
        for (var i= 0, n= this.length; i<n; i++)
            if (i in this && tester.call(that, this[i], i, this))
                return true;
        return false;
    };
}

if (!Object.create) {
    Object.create = (function(){
        function F(){}

        return function(o){
            if (arguments.length != 1) {
                throw new Error('Object.create implementation only accepts one parameter.');
            }
            F.prototype = o;
            return new F()
        }
    })()
}


/**
 * Provides helper objects
 * @module helpers
 * @main helpers
 */



if (typeof String.prototype.startsWith != 'function') {
  String.prototype.startsWith = function (str){
    return this.slice(0, str.length) == str;
  };
}

if (typeof String.prototype.endsWith != 'function') {
  String.prototype.endsWith = function (str){
    return this.slice(-str.length) == str;
  };
}

if (typeof String.prototype.format != 'function') {
	String.prototype.format = function(){
		var args = [this];
		for ( var i=0; i < arguments.length ; i++){
			args.push(arguments[i]);
		}
		return sprintf.apply(null,args);
	};
}


/**
 * Converts `arguments` object into Array.
 * @method asArray
 * @public
 * @param {arguments} argumentsObject
 * @param {Integer} start, optional.
 * @return {Array}
 */
var asArray = function(argumentsObject,start){
	if (!start){start = 0;}
	return Array.prototype.slice.call(argumentsObject, start);
};

var isFunction = function( obj ) {
	return typeof obj === "function";
};

var isWindow = function( obj ) {
	return obj != null && obj == obj.window;
};

//Check it
var isPlainObject = function( obj ) {
	var key;

	// Must be an Object.
	// Because of IE, we also have to check the presence of the constructor property.
	// Make sure that DOM nodes and window objects don't pass through, as well
	if ( !obj || typeof obj !== "object" || obj.nodeType || isWindow( obj ) ) {
		return false;
	}

	try {
		// Not own constructor property must be Object
		if ( obj.constructor &&
			!Object.hasOwnProperty.call(obj, "constructor") &&
			!Object.hasOwnProperty.call(obj.constructor.prototype, "isPrototypeOf") ) {
			return false;
		}
	} catch ( e ) {
		// IE8,9 Will throw exceptions on certain host objects #9897
		return false;
	}

	// // Support: IE<9
	// // Handle iteration over inherited properties before own properties.
	// if ( jQuery.support.ownLast ) {
		// for ( key in obj ) {
			// return Object.hasOwnProperty.call( obj, key );
		// }
	// }

	// Own properties are enumerated firstly, so to speed up,
	// if last one is own, then all properties are own.
	for ( key in obj ) {}

	return key === undefined || Object.hasOwnProperty.call( obj, key );
};

var isInstanceOf = function(obj,cls){
	if (typeof obj === 'string' && cls===String) return true;
	if (typeof obj === 'number' && cls===Number) return true;
	if (obj instanceof cls) return true;
	if (obj['isInstanceOf']) return obj.isInstanceOf(cls);
	return false;
};


var isArray = Array.isArray || function( obj ) {
	return Object.prototype.toString.call( someVar ) === '[object Array]';
};

function extend() {
	var src, copyIsArray, copy, name, options, clone,
		target = arguments[0] || {},
		i = 1,
		length = arguments.length,
		deep = false;

	// Handle a deep copy situation
	if ( typeof target === "boolean" ) {
		deep = target;
		target = arguments[1] || {};
		// skip the boolean and the target
		i = 2;
	}

	// Handle case when target is a string or something (possible in deep copy)
	if ( typeof target !== "object" && !isFunction(target) ) {
		target = {};
	}

	if ( length === i ) {
		target = this;
		--i;
	}

	for ( ; i < length; i++ ) {
		// Only deal with non-null/undefined values
		if ( (options = arguments[ i ]) != null ) {
			// Extend the base object
			for ( name in options ) {
				src = target[ name ];
				copy = options[ name ];

				// Prevent never-ending loop
				if ( target === copy ) {
					continue;
				}

				// Recurse if we're merging plain objects or arrays
				if ( deep && copy && ( isPlainObject(copy) || (copyIsArray = isArray(copy)) ) ) {
					if ( copyIsArray ) {
						copyIsArray = false;
						clone = src && isArray(src) ? src : [];

					} else {
						clone = src && isPlainObject(src) ? src : {};
					}

					// Never move original objects, clone them
					target[ name ] = extend( deep, clone, copy );

				// Don't bring in undefined values
				} else if ( copy !== undefined ) {
					target[ name ] = copy;
				}
			}
		}
	}

	// Return the modified object
	return target;
};


var Namespace = function(ns) {
	var namespaces = ns.split('.');
	var trailing = window;
	for (var i = 0, n = namespaces.length; i < n; i++) {
		if (trailing[namespaces[i]] == undefined){
			trailing[namespaces[i]] = {};
		}
		trailing = trailing[namespaces[i]];
	}
	return trailing;
};




Namespace('joop');


/**
Provides the base oop utilities.

@module joop
**/

var Class = function(){
	var definitions = asArray(arguments);
	var className = definitions[0];

	if (typeof className != 'string'){
		throw 'Class Name was not provided';
	}

	var classConstructor = eval('window.%s = function (){ \
				this.__class__ = %s; \
				%s.prototype.__init__.apply(this,arguments); \
			};%s'.format(className,className,className,className));

	classConstructor.prototype = Object.create(joop.Object.prototype);

	// Inheritance
	var bases = definitions.filter(function(item,index,arr){
		return index > 0 && index < arr.length - 1;
	});
	if(bases.length <= 0 && className != 'joop.Object'){
		bases = [joop.Object];
	}
	for (var i in bases){
		if (bases[i] == undefined){
			throw 'Invalid base class: %s'.format(bases[i]);
		}
		var baseClass = bases[i];
		if (typeof baseClass == 'string'){
			baseClass = eval(baseClass);
		}
		// Static members
		extend(classConstructor,baseClass,{prototype:classConstructor.prototype});
		// Prototype
		classConstructor.prototype = extend(false, classConstructor.prototype, Object.create(baseClass.prototype));
	}

	// Class codes
	classConstructor.prototype = extend(false, {},classConstructor.prototype, definitions[definitions.length-1],{
		constructor: classConstructor
	});

	// Static members
	extend(classConstructor,{
		__name__: className,
		__base_classes__ : bases,
		StaticMembers : function(members){
			return extend(classConstructor,members);
		}
	});

	return eval(className); // classConstructor;
};










var Singleton = function(){
	var definitions = asArray(arguments);
	var className = definitions[0];
	var constructor = Class.apply(
		this, // or null
		arguments);
	var instance = new constructor();
	eval('%s = instance;'.format(className));
	return instance;
};



Class('joop.Object',{
	__init__ : function(){ /* coyote.Object */},
	callSuper: function(cls,functionName,args){
	    if (args == undefined){
	        args = [];
	    }
		return cls.prototype[functionName].apply(this,args);
	},
	__repr__: function(){
		return this.__class__.__name__;
	},
	isInstanceOf: function (cls){
		return this.__class__.isSubclassOf(cls);
	}
}).StaticMembers({
	isSubclassOf: function (cls){
		if (this.__name__ == cls.__name__) return true;
		for (var index=0, n = this.__base_classes__.length; index < n; index++){
			var base = this.__base_classes__[index];
			if ( base.isSubclassOf.apply(base,[cls])){
				return true;
			}
		}
		return false;
	}
});
