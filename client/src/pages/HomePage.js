import React from 'react';
import { Container, Button, Row, Col } from 'react-bootstrap';
import { Link } from 'react-router-dom';

const HomePage = () => {
  return (
    <div className="home-page">
      <div className="p-5 mb-5 bg-light rounded-3 text-center">
        <Container>
          <h1 className="display-4">Welcome to PuzzleVerse</h1>
          <p className="lead">
            A comprehensive MERN stack application designed for LLM training with challenging programming tasks.
          </p>
          <hr className="my-4" />
          <p>
            This project includes 10 independent tasks, each designed to test and improve the capabilities of large language models.
          </p>
          <div className="mt-4">
            <Link to="/tasks" className="btn btn-primary btn-lg me-3">
              View Tasks
            </Link>
            <a
              href="https://github.com/yourusername/puzzleverse-mern"
              target="_blank"
              rel="noopener noreferrer"
              className="btn btn-outline-secondary btn-lg"
            >
              GitHub Repository
            </a>
          </div>
        </Container>
      </div>

      <Container className="features">
        <h2 className="text-center mb-5">Features</h2>
        <Row>
          <Col md={4} className="mb-4">
            <div className="text-center p-4 border rounded h-100">
              <h3>Full-Stack</h3>
              <p>
                Built with the MERN stack (MongoDB, Express, React, Node.js) for a complete web application experience.
              </p>
            </div>
          </Col>
          <Col md={4} className="mb-4">
            <div className="text-center p-4 border rounded h-100">
              <h3>Task-Based</h3>
              <p>
                10 independent tasks, each requiring significant code changes and testing.
              </p>
            </div>
          </Col>
          <Col md={4} className="mb-4">
            <div className="text-center p-4 border rounded h-100">
              <h3>Dockerized</h3>
              <p>
                Easy setup and deployment with Docker and Docker Compose for consistent environments.
              </p>
            </div>
          </Col>
        </Row>
      </Container>

      <Container className="mt-5 text-center">
        <h2>Ready to Get Started?</h2>
        <p className="lead mb-4">
          Clone the repository and start working on the tasks today!
        </p>
        <pre className="bg-dark text-light p-3 rounded text-left d-inline-block">
          <code>{
            'git clone https://github.com/yourusername/puzzleverse-mern.git\n' +
            'cd puzzleverse-mern\n' +
            'npm install\n' +
            'cd client\n' +
            'npm install\n' +
            'cd ..\n' +
            'npm run dev'
          }</code>
        </pre>
      </Container>
    </div>
  );
};

export default HomePage;
