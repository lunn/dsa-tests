/* Display the status of the relays and manipulate them */

/* This program is based loosely on one of the examples. */

#include <stdio.h>
#include <stdbool.h>
#include <stdlib.h>
#include <getopt.h>
#include <unistd.h>

#include <phidget21.h>

/* Display the properties of the attached phidget.  The name, serial
 * number and version of the attached device will be shown. It also
 * display the number of inputs, outputs */
static void
display_properties(const CPhidgetInterfaceKitHandle phid)
{
	int serialNo, version, numOutputs;

	CPhidget_getSerialNumber((CPhidgetHandle)phid, &serialNo);
	CPhidget_getDeviceVersion((CPhidgetHandle)phid, &version);

	CPhidgetInterfaceKit_getOutputCount(phid, &numOutputs);

	printf("Serial Number: %10d\nVersion: %8d\n", serialNo, version);
	printf("Digital Outputs: %d\n", numOutputs);
}

static void
show_one_status(const CPhidgetInterfaceKitHandle phid, const int relay)
{
	int state;

	CPhidgetInterfaceKit_getOutputState(phid, relay, &state);
	
	printf("Relay %d, %s\n", relay, (state == PTRUE ? "On" : "Off"));
}


static void
show_status(const CPhidgetInterfaceKitHandle phid, const int relay)
{
	int outputs;
	int i;

	// Display the properties of the attached interface kit device
	display_properties(phid);

	CPhidgetInterfaceKit_getOutputCount(phid, &outputs);
	
	if (relay == -1) {
		for (i=0; i < outputs; i++)
			show_one_status(phid, i);
	} else {
		show_one_status(phid, relay);
	}
}

static void
set_output(const CPhidgetInterfaceKitHandle phid, const int relay,
	   const int state)
{
	CPhidgetInterfaceKit_setOutputState(phid, relay, state);
}

static void
usage(void)
{
	fprintf(stderr, 
"relay {-s/--status} {-0/--off} {-1/--on} {-t/--toggle} {-r/--relay <relay>}\n"
"\n"
"    {-s/--status}        Show the status of the relays\n"
"    {-1/--on}            Turn on one particular relay\n"
"    {-0/--off}           Turn off one particular relay\n"
"    {-t/--toggle}        Turn a relay off, pause, on\n"
"    {-r/--relay <relay>} Which relay to act on, 0-3\n");
	exit (EXIT_FAILURE);
}


int
main(int argc, char* argv[])
{
	CPhidgetInterfaceKitHandle phid;
	int option_index = 0;
	const char *err;
	int result;
	int c;
	bool do_status = false;
	bool do_off = false;
	bool do_on = false;
	bool do_toggle = false;
	int relay = -1;

	while (1) {
		static struct option long_options[] = {
			{ "status",  no_argument,       0, 's' },
			{ "off",     no_argument,       0, '0' },
			{ "on",      no_argument,       0, '1' },
			{ "toggle",  no_argument,       0, 't' },
			{ "relay",   required_argument, 0, 'r' },
			{ "help",    no_argument,       0, 'h' },
			{ 0,         0,                 0,  0  },
		};
		
		c = getopt_long(argc, argv, "hs10tr:",
				long_options, &option_index);
		
		if (c == -1)
			break;

		switch (c) {
		case 's':
			do_status = true;
			break;
		case '0':
			do_off = true;
			break;
		case '1':
			do_on = true;
			break;
		case 't':
			do_toggle = true;
			break;
		case 'r':
			relay = atol(optarg);
			if (relay < 0 || relay > 3) {
				usage();
				exit (EXIT_FAILURE);
			}
			break;
		case 'h':
		default:
			usage();
			exit (EXIT_FAILURE);
		}
	}
	
	if (!(do_status || do_on || do_off || do_toggle)) {
		usage();
		exit (EXIT_FAILURE);
	}

	CPhidgetInterfaceKit_create(&phid);
	CPhidget_open((CPhidgetHandle)phid, -1);

	// Wait for an interface kit device to be attached
	result = CPhidget_waitForAttachment((CPhidgetHandle)phid, 10000);
	if (result)
	{
		CPhidget_getErrorDescription(result, &err);
		printf("Problem waiting for attachment: %s\n", err);
		exit (EXIT_FAILURE);
	}

	if (do_status) {
		show_status(phid, relay);
	}
	
	if ((do_off || do_on| do_toggle) && (relay == -1)) {
		usage();
		exit (EXIT_FAILURE);
	}

	if (do_off) {
		set_output(phid, relay, PFALSE);
	}

	if (do_on) {
		set_output(phid, relay, PTRUE);
	}

	/* We assume here the state is already off. Toggle on, pause
	   for a second, toggle off. */
	if (do_toggle) {
		set_output(phid, relay, PTRUE);
		sleep(1);
		set_output(phid, relay, PFALSE);
	}
	
	CPhidget_close((CPhidgetHandle)phid);
	CPhidget_delete((CPhidgetHandle)phid);
	
	exit (EXIT_SUCCESS);
}


