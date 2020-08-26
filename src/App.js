import React, { useState, useEffect } from 'react';
import logo from './logo.svg';
import './App.css';
import AppBar from '@material-ui/core/AppBar';
import IconButton from '@material-ui/core/IconButton';
import Toolbar from '@material-ui/core/Toolbar';
import Typography from '@material-ui/core/Typography';
import MenuIcon from '@material-ui/icons/Menu';
import { makeStyles } from '@material-ui/core/styles';
import MyTable from './components/MyTable';
import { Container } from "reactstrap"
import "bootstrap/dist/css/bootstrap.min.css"

function NavBar(props) {

	useEffect(() => {
		   document.title = "loldat"
	}, []);

	return (<AppBar position="static">
		  <Toolbar variant="dense">
		    <IconButton edge="start" color="inherit" aria-label="menu">
		      <MenuIcon />
		    </IconButton>
		    <Typography variant="h6" color="inherit">
		    Hell yeah brøther
		    </Typography>
		  </Toolbar>
		</AppBar>)
}

function App() {

    //For our teams table.
    const [teamData, setTeamData] = useState(0);

    useEffect(() => {
    fetch('/api/get_team_data').then(res => res.json()).then(data => {
          setTeamData(data);
        });
    }, []);

    const data = Array.from(teamData);
    console.dir(data);

    const columns = [
        { Header: "Day Played", accessor: (values) => {
		const day = values.start_time.substring(0, 10);
	    return day
	}, width: "5%"},
	//
        { Header: "Game Version", accessor: (values) => {
	    var vers = "";
	    console.log(values.game_version !== null);
	    if (values.game_version !== null)
	    {
		    //Capture the first 2 sections of game version
		    let re = new RegExp(/(\d*.\d*\.)/g);
		    vers = values.game_version.match(re)[0];
		    vers = vers.substring(0, vers.length-1);
	    }
	    return vers
	}, width: "4%"},
        { Header: "Participants", accessor: "participants", width: "10%"},
        { Header: "First Blood", accessor: "first_blood", width: "3%"},
        { Header: "First Dragon", accessor: "first_dragon", width: "3%"},
        { Header: "First Tower", accessor: "first_tower", width: "3%"},
        { Header: "First Herald", accessor: "first_rift_herald", width: "3%"},
        { Header: "First Inhib", accessor: "first_inhib", width: "3%"},
        { Header: "Ally Dragon Kills", accessor: "ally_dragon_kills", width: "3%"},
        { Header: "Ally Rift Heralds", accessor: "ally_rift_herald_kills", width: "3%"},
        { Header: "Enemy Dragon Kills", accessor: "enemy_dragon_kills", width: "3%"},
        { Header: "Enemy Rift Heralds", accessor: "enemy_rift_herald_kills", width: "3%"},
        { Header: "Inhibs", accessor: "inhib_kills", width: "3%"},
        { Header: "Allies", accessor: "allies", width: "10%"},
        { Header: "Enemies", accessor: "enemies", width: "10%"},
        { Header: "Wonned?", accessor: (values) => {
	    const bool = values.win == "Win" ? 'True' : 'False';
	    return bool
	    }, width: "3%"}
    ];

    const root = (
		    <div className="App" id="root">
		    <NavBar />
			<MyTable columns={columns} data={data} 
			    getCellProps={cellInfo => ({
			      style: {
			      backgroundColor: ((cellInfo.row.cells[15].value ==="True") ? `rgba(0,255,0,.2)`: `rgba(255,0,0,.2)`)
			    	}})}
			    />
		    </div>
    );

    return root

}

export default App;
