import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Form, Button, InputGroup, FormControl, Card, Container, Row, Col } from 'react-bootstrap';
import { MdFlightTakeoff, MdFlightLand, MdDateRange, MdFlight } from 'react-icons/md';
import './flightSearch.css';
import logo from '../assets/logo.png';

const FlightSearch = () => {
    const [airports, setAirports] = useState([]);
    const [origin, setOrigin] = useState('');
    const [destination, setDestination] = useState('');
    const [date, setDate] = useState('');
    const [filteredAirportsOrigin, setFilteredAirportsOrigin] = useState([]);
    const [filteredAirportsDestination, setFilteredAirportsDestination] = useState([]);
    const [results, setResults] = useState(null);
    const [loading, setLoading] = useState(false);
    const [showModal, setShowModalIndex] = useState(null);

    // Fetch airports from the backend
    useEffect(() => {
        const fetchAirports = async () => {
            try {
                const response = await axios.get('http://127.0.0.1:8000/api/flights/airports/');
                setAirports(response.data);
            } catch (err) {
                console.error('Error fetching airports:', err);
            }
        };
        fetchAirports();
    }, []);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);

        const originCode = airports.find(airport => airport.name === origin)?.code;
        const destinationCode = airports.find(airport => airport.name === destination)?.code;

        try {
            await new Promise((resolve) => setTimeout(resolve, 2000)); // Esperar 2 segundos para mostrar el loader
            const response = await axios.get('http://127.0.0.1:8000/api/flights/search/', {
                params: {
                    origin: originCode,
                    destination: destinationCode,
                    date,
                },
            });
            setResults(response.data);
        } catch (err) {
            console.error(err);
            setResults({ error: 'Error al buscar los vuelos. Intenta nuevamente.' });
        } finally {
            setLoading(false);
        }
    };

    const handleOriginChange = (e) => {
        const value = e.target.value;
        setOrigin(value);
        setFilteredAirportsOrigin(
            airports.filter((airport) =>
                airport.name.toLowerCase().includes(value.toLowerCase()) || airport.code.toLowerCase().includes(value.toLowerCase())
            )
        );
    };

    const handleDestinationChange = (e) => {
        const value = e.target.value;
        setDestination(value);
        setFilteredAirportsDestination(
            airports.filter((airport) =>
                airport.name.toLowerCase().includes(value.toLowerCase()) || airport.code.toLowerCase().includes(value.toLowerCase())
            )
        );
    };

    const handleSelectOrigin = (name) => {
        setOrigin(name);
        setFilteredAirportsOrigin([]);
    };

    const handleSelectDestination = (name) => {
        setDestination(name);
        setFilteredAirportsDestination([]);
    };

    const handleShowModal = (index) => {
        setShowModalIndex(index);
    };

    const handleCloseModal = () => {
        setShowModalIndex(null);
    };

    return (
        <>
            {/* Loader Full Screen */}
            {loading && (
                <div className="loader-overlay">
                    <div className="plane-loader">
                        <div className="plane"></div>
                        <div className="cloud cloud1"></div>
                        <div className="cloud cloud2 animated"></div>
                        <div className="cloud cloud3 animated"></div>
                    </div>
                </div>
            )}

            {/* Logo */}
            <header className="header mb-4">
                <img
                    src={logo}
                    width="150"
                    height="60"
                    alt="Logo Portal de Pago Air"
                    className="logo-left"
                />
            </header>

            {/* Hero Section */}
            <div className="hero-section">
                <Container>
                    <div className="hero-content">
                        <h1 className="mb-4">Explora el mundo y disfruta de su belleza</h1>
                        <p className="mb-5">Encuentra y comparte tus experiencias alrededor del mundo.</p>
                    </div>
                    <div className="search-card">
                        <Form onSubmit={handleSubmit} className="w-100">
                            <div className="d-flex flex-wrap gap-3 justify-content-center">
                                <InputGroup className="mb-3" style={{ maxWidth: '260px' }}>
                                    <InputGroup.Text>
                                        <MdFlightTakeoff />
                                    </InputGroup.Text>
                                    <FormControl
                                        placeholder="Origen"
                                        value={origin}
                                        onChange={handleOriginChange}
                                        required
                                    />
                                    {filteredAirportsOrigin.length > 0 && (
                                        <div className="input-dropdown">
                                            {filteredAirportsOrigin.map((airport) => (
                                                <div
                                                    key={airport.code}
                                                    onClick={() => handleSelectOrigin(airport.name)}
                                                    className="input-dropdown-item"
                                                >
                                                    {airport.name} - {airport.code}
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                </InputGroup>

                                <InputGroup className="mb-3" style={{ maxWidth: '260px' }}>
                                    <InputGroup.Text>
                                        <MdFlightLand />
                                    </InputGroup.Text>
                                    <FormControl
                                        placeholder="Destino"
                                        value={destination}
                                        onChange={handleDestinationChange}
                                        required
                                    />
                                    {filteredAirportsDestination.length > 0 && (
                                        <div className="input-dropdown">
                                            {filteredAirportsDestination.map((airport) => (
                                                <div
                                                    key={airport.code}
                                                    onClick={() => handleSelectDestination(airport.name)}
                                                    className="input-dropdown-item"
                                                >
                                                    {airport.name} - {airport.code}
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                </InputGroup>

                                <InputGroup className="mb-3" style={{ maxWidth: '200px' }}>
                                    <InputGroup.Text>
                                        <MdDateRange />
                                    </InputGroup.Text>
                                    <FormControl
                                        type="date"
                                        value={date}
                                        onChange={(e) => setDate(e.target.value)}
                                        required
                                    />
                                </InputGroup>

                                <Button
                                    type="submit"
                                    className="mb-3 btn-search"
                                    disabled={loading}
                                >
                                    {loading ? 'Buscando...' : 'Buscar'}
                                </Button>
                            </div>
                        </Form>
                    </div>
                </Container>
            </div>

            {/* Resultados */}
            {results && (
                <div className="results-container">
                    <Container className="mt-5 mb-5">
                        <h2 className="mb-5">Vuelos desde {origin} hacia {destination}</h2>
                        <Row className="g-4">
                            {results.direct_flights && results.direct_flights.length > 0 && results.direct_flights.map((flight, index) => (
                                <Col key={index} md={4}>
                                    <Card className="card-flight">
                                        <div className="d-flex justify-content-between align-items-center mb-3">
                                            <div style={{ textAlign: 'left' }}>
                                                <h5 className="flight-info-header">{flight.departure_time}</h5>
                                                <span className="flight-info-sub">{flight.origin.code}</span>
                                            </div>
                                            <div style={{ textAlign: 'right' }}>
                                                <h5 className="flight-info-header">{flight.arrival_time}</h5>
                                                <span className="flight-info-sub">{flight.destination.code}</span>
                                            </div>
                                        </div>
                                        <div className="text-center mb-3">
                                            <div className="flight-type">Directo</div>
                                            <div className="d-flex align-items-center justify-content-center mt-3">
                                                <div className="flight-details-divider"></div>
                                                <MdFlight className="flight-details-icon" />
                                                <div className="flight-details-divider"></div>
                                            </div>
                                            <div className="flight-duration">{flight.duration}</div>
                                        </div>
                                    </Card>
                                </Col>
                            ))}

                            {results.routes_with_stops && results.routes_with_stops.length > 0 && results.routes_with_stops.map((route, index) => (
                                <Col key={index} md={4}>
                                    <Card className="card-flight" style={{ position: 'relative' }}>
                                        <div className="d-flex justify-content-between align-items-center mb-3">
                                            <div style={{ textAlign: 'left' }}>
                                                <h5 className="flight-info-header">{route.flights[0].departure_time.split(' ')[1]}</h5>
                                                <span className="flight-info-sub">{route.flights[0].origin}</span>
                                            </div>
                                            <div style={{ textAlign: 'right' }}>
                                                <h5 className="flight-info-header">{route.flights[route.flights.length - 1].arrival_time.split(' ')[1]}</h5>
                                                <span className="flight-info-sub">{route.flights[route.flights.length - 1].destination}</span>
                                            </div>
                                        </div>
                                        <div
                                            className="route-duration position-relative text-center"
                                            onMouseEnter={() => handleShowModal(index)}
                                            onMouseLeave={handleCloseModal}
                                        >
                                            {route.flights.length - 1} Escala{route.flights.length - 1 > 1 ? 's' : ''}
                                            {showModal === index && (
                                                <div className="tooltip-details">
                                                    <h6 className="fw-bold text-center">Detalles del vuelo</h6>
                                                    {route.flights.map((flight, idx) => (
                                                        <div key={idx} className="mb-3">
                                                            <div className="d-flex justify-content-between align-items-center text-dark">
                                                                <span style={{ fontWeight: 'bold' }}>
                                                                    {flight.departure_time.split(' ')[1]} <span className='fw-normal'>{flight.origin}</span>
                                                                </span>
                                                                <MdFlight className="flight-details-icon" />
                                                                
                                                                <span style={{ fontWeight: 'bold', textAlign: 'right' }}>
                                                                    {flight.arrival_time.split(' ')[1]} <span className='fw-normal'>{flight.destination}</span>
                                                                </span>
                                                            </div>
                                                        </div>
                                                    ))}
                                                    <div style={{ fontSize: '1rem', fontWeight: 'normal', textAlign: 'center', color: '#12ab70' }}>
                                                        {route.total_duration}
                                                    </div>
                                                </div>
                                            )}
                                        </div>
                                        <div className="d-flex align-items-center justify-content-center mt-3">
                                            <div className="flight-details-divider"></div>
                                            <MdFlight className="flight-details-icon" />
                                            <div className="flight-details-divider"></div>
                                        </div>
                                        <div className="flight-duration text-center">{route.total_duration}</div>
                                    </Card>
                                </Col>
                            ))}



                        </Row>
                        {results.direct_flights.length === 0 && results.routes_with_stops.length === 0 && (
                            <div className="no-flights-message">
                                <Card className="no-flights-card text-center p-4 mt-3">
                                    <Card.Body>
                                        <Card.Title className='text-dark display-5 fw-bold'>No hay vuelos disponibles</Card.Title>
                                        <Card.Text>
                                            <p className='badge bg-danger'>Intenta con otra fecha o destino.</p>
                                        </Card.Text>
                                    </Card.Body>

                                </Card>
                            </div>
                        )}
                    </Container>
                    
                </div>
                
            )}

            {/* Footer */}
            <footer className="footer">
                <Container>
                    <p>© 2024 Portal de Pago Air. Todos los derechos reservados.</p>
                </Container>
            </footer>
        </>
    );
};

export default FlightSearch;
